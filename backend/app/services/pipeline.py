import io
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import HTTPException
from sqlalchemy.orm import Session
from thefuzz import fuzz

from app.core.config import settings
from app.models import (
    BulletCitation,
    DeckBullet,
    DeckSection,
    DeckSubsection,
    Document,
    DocumentImage,
    DocumentStatus,
    Job,
    JobStatus,
    SourceSpan,
)
from app.services.llm import LLMClient, FactCandidate
from app.services.pdf_parser import ParsedChunk, ParsedImage, parse_pdf_bytes

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _detect_language(chunks: list[ParsedChunk]) -> str:
    """Detect source document language from initial chunks."""
    try:
        from langdetect import detect
        sample = " ".join(c.text[:500] for c in chunks[:5])
        return detect(sample)
    except Exception:  # noqa: BLE001
        return "en"


def _fuzzy_dedupe(facts: list[FactCandidate], threshold: int) -> list[FactCandidate]:
    """Deduplicate facts using fuzzy string matching. Keep higher-importance variant."""
    kept: list[FactCandidate] = []
    kept_lower: list[str] = []
    kept_lengths: list[int] = []
    # Length-based early rejection: if lengths differ by too much,
    # token_sort_ratio cannot exceed the threshold.
    max_len_ratio = threshold / 100.0  # e.g. 0.86

    for f in facts:
        f_lower = f.statement.lower()
        f_len = len(f_lower)
        is_dup = False
        for i, existing_lower in enumerate(kept_lower):
            # Quick length check: if shorter/longer ratio < threshold, skip
            e_len = kept_lengths[i]
            if e_len > 0 and f_len > 0:
                ratio_len = min(f_len, e_len) / max(f_len, e_len)
                if ratio_len < max_len_ratio:
                    continue
            ratio = fuzz.token_sort_ratio(f_lower, existing_lower)
            if ratio >= threshold:
                is_dup = True
                if f.importance > kept[i].importance:
                    kept[i] = f
                    kept_lower[i] = f_lower
                    kept_lengths[i] = f_len
                break
        if not is_dup:
            kept.append(f)
            kept_lower.append(f_lower)
            kept_lengths.append(f_len)
    return kept


def _find_best_snippet(statement: str, chunk_text: str, max_len: int = 180) -> str:
    """Find the most relevant snippet from chunk_text for the given statement using keyword overlap."""
    if len(chunk_text) <= max_len:
        return chunk_text

    # Extract keywords from statement (words longer than 3 chars)
    keywords = {w.lower() for w in statement.split() if len(w) > 3}
    if not keywords:
        return chunk_text[:max_len]

    best_score = -1
    best_start = 0
    step = 40

    for start in range(0, len(chunk_text) - max_len + 1, step):
        window = chunk_text[start : start + max_len].lower()
        score = sum(1 for kw in keywords if kw in window)
        if score > best_score:
            best_score = score
            best_start = start

    snippet = chunk_text[best_start : best_start + max_len]
    # Try to start at a word boundary
    if best_start > 0:
        space = snippet.find(" ")
        if space != -1 and space < 20:
            snippet = snippet[space + 1 :]
    return snippet.strip()


def _process_images(
    db: Session,
    doc: Document,
    images: list[ParsedImage],
) -> list[DocumentImage]:
    """Process extracted images: detect formulas and upload to storage in parallel, then save DB records."""
    from app.services.formula import detect_formula
    from app.services.storage import upload_fileobj

    doc_images: list[DocumentImage] = []

    # Run formula detection AND upload in parallel per image
    def _process_one(img: ParsedImage) -> tuple[str, str | None, str, bool]:
        """Returns (image_id, latex, storage_key, upload_ok)."""
        latex = detect_formula(img.image_bytes)
        storage_key = f"documents/{doc.id}/images/{img.image_id}.{img.ext}"
        upload_ok = True
        try:
            upload_fileobj(io.BytesIO(img.image_bytes), storage_key)
        except Exception:  # noqa: BLE001
            logger.warning("Failed to upload image %s", img.image_id)
            upload_ok = False
        return img.image_id, latex, storage_key, upload_ok

    results: dict[str, tuple[str | None, str, bool]] = {}
    max_workers = min(4, max(1, len(images)))
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_process_one, img): img for img in images}
        for future in as_completed(futures):
            img = futures[future]
            try:
                img_id, latex, storage_key, upload_ok = future.result()
                results[img_id] = (latex, storage_key, upload_ok)
            except Exception:  # noqa: BLE001
                results[img.image_id] = (None, "", False)

    # Save DB records (must be on main thread for session safety)
    for img in images:
        result = results.get(img.image_id)
        if not result or not result[2]:  # upload failed
            continue

        latex, storage_key, _ = result
        is_formula = latex is not None

        doc_image = DocumentImage(
            document_id=doc.id,
            page=img.page,
            image_index=img.image_index,
            storage_key=storage_key,
            width=img.width,
            height=img.height,
            is_formula=is_formula,
            latex=latex,
        )
        db.add(doc_image)
        doc_images.append(doc_image)

    if doc_images:
        db.flush()
    db.commit()
    return doc_images


class PipelineService:
    def __init__(self):
        self.llm = LLMClient()

    def _set_job(self, db: Session, job: Job, *, status: JobStatus | None = None, progress: float | None = None):
        if status is not None:
            job.status = status
        if progress is not None:
            job.progress = progress
        db.add(job)
        db.commit()
        db.refresh(job)

    def _load_document_or_404(self, db: Session, document_id: str) -> Document:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")
        return doc

    def run(self, db: Session, document_id: str, job_id: str, file_bytes: bytes) -> None:
        doc = self._load_document_or_404(db, document_id)
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise PipelineError("JOB_NOT_FOUND", "job missing")

        try:
            self._set_job(db, job, status=JobStatus.running, progress=0.05)
            doc.status = DocumentStatus.processing
            db.add(doc)
            db.commit()

            # Step 1-2: ingest + parse
            try:
                pages, chunks, images = parse_pdf_bytes(file_bytes)
            except ValueError as exc:
                raise PipelineError("PARSE_FAILED", str(exc)) from exc
            if pages > settings.max_pages:
                raise PipelineError("DOC_TOO_LARGE", f"pages={pages}")
            doc.pages = pages
            self._set_job(db, job, progress=0.15)

            # Step 2b: language detection
            language = _detect_language(chunks)
            doc.language = language
            db.add(doc)
            db.commit()
            self._set_job(db, job, progress=0.2)

            # Step 2c: extract & classify images
            doc_images: list[DocumentImage] = []
            if images:
                doc_images = _process_images(db, doc, images)
                logger.info("Extracted %d images (%d formulas) from document %s",
                            len(doc_images),
                            sum(1 for di in doc_images if di.is_formula),
                            doc.id)
            self._set_job(db, job, progress=0.25)

            # Build formula facts from detected LaTeX
            formula_facts: list[FactCandidate] = []
            formula_image_map: dict[str, DocumentImage] = {}  # fact_id -> DocumentImage
            for di in doc_images:
                if di.is_formula and di.latex:
                    fact_id = f"formula_{di.id}"
                    formula_facts.append(
                        FactCandidate(
                            fact_id=fact_id,
                            chunk_id=f"c_img_{di.page:04d}",
                            statement=f"Formula on page {di.page}: ${di.latex}$",
                            importance=5,
                            keywords=[],
                        )
                    )
                    formula_image_map[fact_id] = di

            # Step 3: extract facts (parallel)
            facts: list[FactCandidate] = []
            errors: list[str] = []
            max_workers = min(8, len(chunks))

            def _extract_one(c: ParsedChunk) -> list[FactCandidate]:
                return self.llm.extract_facts(c.chunk_id, c.text)

            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                future_to_chunk = {pool.submit(_extract_one, c): c for c in chunks}
                for future in as_completed(future_to_chunk):
                    try:
                        facts.extend(future.result())
                    except ValueError as exc:
                        errors.append(str(exc))
            if errors and not facts:
                raise PipelineError("LLM_OUTPUT_INVALID", errors[0])

            # Append formula facts
            facts.extend(formula_facts)
            self._set_job(db, job, progress=0.35)

            # Step 4: fuzzy merge/dedupe
            chunk_map = {c.chunk_id: c for c in chunks}
            fact_to_chunk: dict[str, ParsedChunk] = {}
            for f in facts:
                if f.chunk_id in chunk_map:
                    fact_to_chunk[f.fact_id] = chunk_map[f.chunk_id]

            threshold = int(settings.dedupe_threshold * 100)
            merged_facts = _fuzzy_dedupe(facts, threshold)
            self._set_job(db, job, progress=0.5)

            # Step 5: LLM outline building
            try:
                outline = self.llm.build_outline(merged_facts, language)
            except Exception as exc:
                raise PipelineError("LLM_OUTPUT_INVALID", f"Outline generation failed: {exc}") from exc
            self._set_job(db, job, progress=0.65)

            # Step 6: LLM annotation writing
            sections_data = []
            for sec in outline.sections:
                sub_data = []
                for sub in sec.subsections:
                    bullet_texts = [merged_facts[i].statement for i in sub.fact_indices if i < len(merged_facts)]
                    sub_data.append({"heading": sub.heading, "bullet_texts": bullet_texts})
                sections_data.append({"heading": sec.heading, "subsections": sub_data})

            annotations = self.llm.write_annotations(sections_data, language)
            self._set_job(db, job, progress=0.75)

            # Step 7: persist outline + citations + quality gate
            db.query(DeckSection).filter(DeckSection.document_id == doc.id).delete()
            db.query(SourceSpan).filter(SourceSpan.document_id == doc.id).delete()
            db.commit()

            all_bullets = 0
            cited_bullets = 0
            used_fact_ids: set[str] = set()
            annotation_idx = 0

            for s_idx, sec in enumerate(outline.sections):
                section = DeckSection(
                    document_id=doc.id,
                    heading=sec.heading,
                    summary_note=sec.summary_note,
                    sort_index=s_idx,
                )
                db.add(section)
                db.flush()  # need section.id for subsections

                subsections_batch = []
                for ss_idx, sub in enumerate(sec.subsections):
                    ann = ""
                    if annotation_idx < len(annotations):
                        ann = annotations[annotation_idx]
                    annotation_idx += 1

                    subsection = DeckSubsection(
                        section_id=section.id,
                        heading=sub.heading,
                        annotation=ann,
                        sort_index=ss_idx,
                    )
                    subsections_batch.append((subsection, sub))

                db.add_all([s for s, _ in subsections_batch])
                db.flush()  # need subsection.id for bullets

                # Collect all bullets, spans, citations for this section
                pending_bullets = []
                for subsection, sub in subsections_batch:
                    for b_idx, fact_idx in enumerate(sub.fact_indices):
                        if fact_idx >= len(merged_facts):
                            continue
                        mf = merged_facts[fact_idx]
                        linked_image = formula_image_map.get(mf.fact_id)

                        bullet = DeckBullet(
                            subsection_id=subsection.id,
                            text=mf.statement,
                            sort_index=b_idx,
                            image_id=linked_image.id if linked_image else None,
                        )
                        pending_bullets.append((bullet, mf, linked_image))
                        all_bullets += 1
                        used_fact_ids.add(mf.fact_id)

                db.add_all([b for b, _, _ in pending_bullets])
                db.flush()  # need bullet.id for citations

                # Build spans and citations in batch
                pending_spans = []
                span_to_bullet = []
                for bullet, mf, linked_image in pending_bullets:
                    src_chunk = fact_to_chunk.get(mf.fact_id)
                    if src_chunk:
                        snippet = _find_best_snippet(mf.statement, src_chunk.text)
                        span = SourceSpan(
                            document_id=doc.id,
                            page=src_chunk.page,
                            paragraph_index=src_chunk.paragraph_index,
                            quote_snippet=snippet,
                            char_start=src_chunk.char_start,
                            char_end=src_chunk.char_end,
                        )
                        pending_spans.append(span)
                        span_to_bullet.append(bullet)
                        cited_bullets += 1
                    elif linked_image:
                        span = SourceSpan(
                            document_id=doc.id,
                            page=linked_image.page,
                            paragraph_index=0,
                            quote_snippet=f"[Formula image on page {linked_image.page}]",
                            char_start=None,
                            char_end=None,
                        )
                        pending_spans.append(span)
                        span_to_bullet.append(bullet)
                        cited_bullets += 1

                if pending_spans:
                    db.add_all(pending_spans)
                    db.flush()  # need span.id for citations
                    db.add_all([
                        BulletCitation(bullet_id=span_to_bullet[i].id, source_span_id=span.id)
                        for i, span in enumerate(pending_spans)
                    ])

            db.commit()
            self._set_job(db, job, progress=0.9)

            # Quality gate
            coverage = (len(used_fact_ids) / len(merged_facts)) if merged_facts else 1.0
            citation_completeness = (cited_bullets / all_bullets) if all_bullets else 1.0

            if citation_completeness < 1.0:
                raise PipelineError("CITATION_INCOMPLETE", "every bullet needs citation")
            if coverage < settings.quality_coverage_threshold:
                raise PipelineError("QUALITY_GATE_FAILED", f"coverage={coverage}")

            job.metrics_json = {
                "coverage_ratio": coverage,
                "citation_completeness": citation_completeness,
                "dedupe_ratio": 1 - (len(merged_facts) / max(1, len(facts))),
            }
            doc.status = DocumentStatus.ready
            self._set_job(db, job, status=JobStatus.done, progress=1.0)
            db.add(doc)
            db.commit()
        except PipelineError as exc:
            job.status = JobStatus.failed
            job.error_code = exc.code
            job.error_detail = exc.detail
            doc.status = DocumentStatus.failed
            db.add_all([job, doc])
            db.commit()
        except Exception as exc:  # noqa: BLE001
            job.status = JobStatus.failed
            err_msg = str(exc)
            if err_msg.startswith("LLM_API_ERROR"):
                job.error_code = "LLM_API_ERROR"
            elif err_msg.startswith("LLM_OUTPUT_INVALID"):
                job.error_code = "LLM_OUTPUT_INVALID"
            else:
                job.error_code = "GEN_TIMEOUT"
            job.error_detail = err_msg
            doc.status = DocumentStatus.failed
            db.add_all([job, doc])
            db.commit()
