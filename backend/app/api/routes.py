import io
import logging
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse, Response
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import (
    DeckBullet,
    DeckSection,
    DeckSubsection,
    Document,
    DocumentImage,
    Job,
    JobStatus,
    SourceSpan,
)
from app.schemas.common import BulletOut, CitationOut, DeckOut, QualityReport, SectionOut, SubsectionOut
from app.schemas.document import DocumentCreateOut, DocumentListItem, DocumentListOut
from app.schemas.edit import DeckPatchRequest
from app.schemas.job import JobOut
from app.services.auth import CurrentUser, get_current_user
from app.services.storage import StorageError, delete_file, read_file_bytes, upload_fileobj
from app.services.pipeline import PipelineService
from app.workers.tasks import process_document

router = APIRouter()
logger = logging.getLogger(__name__)


def _deck_from_db(db: Session, doc: Document) -> DeckOut:
    sections_db = (
        db.query(DeckSection)
        .filter(DeckSection.document_id == doc.id)
        .order_by(DeckSection.sort_index.asc())
        .all()
    )

    sections = []
    for s in sections_db:
        subsections_db = (
            db.query(DeckSubsection)
            .filter(DeckSubsection.section_id == s.id)
            .order_by(DeckSubsection.sort_index.asc())
            .all()
        )

        subsections = []
        for ss in subsections_db:
            bullets_db = (
                db.query(DeckBullet)
                .filter(DeckBullet.subsection_id == ss.id)
                .order_by(DeckBullet.sort_index.asc())
                .all()
            )
            bullets = []
            for b in bullets_db:
                # Direct relationship is easier than ad-hoc join for the scaffold.
                cits = []
                for bc in b.citations:
                    sp = db.query(SourceSpan).filter(SourceSpan.id == bc.source_span_id).first()
                    if sp:
                        cits.append(
                            CitationOut(
                                page=sp.page,
                                paragraph_index=sp.paragraph_index,
                                quote_snippet=sp.quote_snippet,
                            )
                        )
                # Populate image fields from linked DocumentImage
                image_url = None
                latex = None
                if b.image_id:
                    doc_img = db.query(DocumentImage).filter(DocumentImage.id == b.image_id).first()
                    if doc_img:
                        image_url = doc_img.storage_key
                        latex = doc_img.latex

                bullets.append(BulletOut(
                    id=str(b.id),
                    text=b.text,
                    citations=cits,
                    image_url=image_url,
                    latex=latex,
                ))
            subsections.append(
                SubsectionOut(
                    id=str(ss.id),
                    heading=ss.heading,
                    annotation=ss.annotation,
                    bullets=bullets,
                )
            )

        sections.append(
            SectionOut(
                id=str(s.id),
                heading=s.heading,
                summary_note=s.summary_note,
                subsections=subsections,
            )
        )

    latest_job = (
        db.query(Job)
        .filter(Job.document_id == doc.id)
        .order_by(Job.updated_at.desc())
        .first()
    )
    metrics = latest_job.metrics_json if latest_job else {}
    return DeckOut(
        document_id=str(doc.id),
        title=doc.title,
        language=doc.language,
        quality_report=QualityReport(
            coverage_ratio=float(metrics.get("coverage_ratio", 0.0)),
            citation_completeness=float(metrics.get("citation_completeness", 0.0)),
            dedupe_ratio=float(metrics.get("dedupe_ratio", 0.0)),
        ),
        sections=sections,
    )


@router.post("/documents", response_model=DocumentCreateOut)
def create_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="ONLY_PDF_ALLOWED")

    content = file.file.read()
    key = f"documents/{current_user.user_id}/{uuid.uuid4()}.pdf"
    try:
        upload_fileobj(io.BytesIO(content), key)
    except StorageError as exc:
        raise HTTPException(status_code=503, detail=f"STORAGE_ERROR: {exc}") from exc

    doc = Document(owner_id=current_user.user_id, title=file.filename, file_key=key)
    db.add(doc)
    db.flush()

    job = Job(document_id=doc.id, status=JobStatus.queued, progress=0.0)
    db.add(job)
    db.commit()

    try:
        process_document.delay(str(doc.id), str(job.id))
    except Exception as exc:
        logger.warning("Queue dispatch failed; fallback to inline pipeline: %s", exc)
        # Local fallback: run pipeline inline when queue infra is unavailable.
        file_bytes = read_file_bytes(doc.file_key)
        PipelineService().run(db, document_id=str(doc.id), job_id=str(job.id), file_bytes=file_bytes)

    return DocumentCreateOut(document_id=str(doc.id), job_id=str(job.id))


@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="JOB_NOT_FOUND")
    return JobOut(
        id=str(job.id),
        status=job.status.value,
        progress=job.progress,
        error_code=job.error_code,
        error_detail=job.error_detail,
    )


@router.get("/documents", response_model=DocumentListOut)
def list_documents(db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    docs = (
        db.query(Document)
        .filter(Document.owner_id == current_user.user_id)
        .order_by(Document.created_at.desc())
        .all()
    )
    total = db.query(func.count(Document.id)).filter(Document.owner_id == current_user.user_id).scalar() or 0
    return DocumentListOut(
        items=[
            DocumentListItem(
                id=str(d.id),
                title=d.title,
                status=d.status.value,
                pages=d.pages,
                created_at=d.created_at.isoformat(),
            )
            for d in docs
        ],
        total=total,
    )


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")
    if str(doc.owner_id) != current_user.user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    file_key = doc.file_key

    # Collect image storage keys before deletion
    image_keys = [
        img.storage_key
        for img in db.query(DocumentImage).filter(DocumentImage.document_id == document_id).all()
    ]

    # SourceSpan has no cascade relationship — delete manually
    db.query(SourceSpan).filter(SourceSpan.document_id == document_id).delete()
    # DocumentImage cascades from Document, but we collected keys above
    # Document deletion cascades to Jobs, DeckSections, Subsections, Bullets, Citations, DocumentImages
    db.delete(doc)
    db.commit()

    # Delete files from storage
    try:
        delete_file(file_key)
    except StorageError:
        logger.warning("Failed to delete storage object %s", file_key)

    for img_key in image_keys:
        try:
            delete_file(img_key)
        except StorageError:
            logger.warning("Failed to delete image storage object %s", img_key)

    return None


@router.get("/documents/{document_id}/slides", response_model=DeckOut)
def get_slides(document_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")
    if str(doc.owner_id) != current_user.user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    return _deck_from_db(db, doc)


@router.patch("/documents/{document_id}/slides", response_model=DeckOut)
def patch_slides(
    document_id: str,
    payload: DeckPatchRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")
    if str(doc.owner_id) != current_user.user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    for s in payload.sections:
        sec = db.query(DeckSection).filter(DeckSection.id == s.id).first()
        if not sec:
            continue
        if s.heading is not None:
            sec.heading = s.heading
        if s.summary_note is not None:
            sec.summary_note = s.summary_note

        for ss in s.subsections:
            sub = db.query(DeckSubsection).filter(DeckSubsection.id == ss.id).first()
            if not sub:
                continue
            if ss.heading is not None:
                sub.heading = ss.heading
            if ss.annotation is not None:
                sub.annotation = ss.annotation

            for b in ss.bullets:
                bul = db.query(DeckBullet).filter(DeckBullet.id == b.id).first()
                if bul:
                    bul.text = b.text

    db.commit()
    return _deck_from_db(db, doc)


@router.get("/documents/{document_id}/export.md", response_class=PlainTextResponse)
def export_markdown(document_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")
    if str(doc.owner_id) != current_user.user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    deck = _deck_from_db(db, doc)
    lines = [f"# {deck.title}", ""]
    footnotes: list[str] = []
    fn = 1

    for sec in deck.sections:
        lines.append(f"## {sec.heading}")
        if sec.summary_note:
            lines.append(sec.summary_note)
        lines.append("")
        for sub in sec.subsections:
            lines.append(f"### {sub.heading}")
            if sub.annotation:
                lines.append(f"> {sub.annotation}")
            for bullet in sub.bullets:
                markers = []
                for c in bullet.citations:
                    markers.append(f"[^{fn}]")
                    footnotes.append(f"[^{fn}]: p.{c.page} para {c.paragraph_index} - {c.quote_snippet}")
                    fn += 1
                text = bullet.text
                if bullet.latex:
                    text = f"{text} (${bullet.latex}$)"
                lines.append(f"- {text} {' '.join(markers)}".strip())
            lines.append("")

    lines.extend(["", *footnotes])
    return "\n".join(lines)


@router.get("/documents/{document_id}/export.pptx")
def export_pptx(document_id: str, db: Session = Depends(get_db), current_user: CurrentUser = Depends(get_current_user)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")
    if str(doc.owner_id) != current_user.user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    deck = _deck_from_db(db, doc)

    def _image_loader(storage_key: str) -> bytes:
        return read_file_bytes(storage_key)

    from app.services.pptx_export import generate_pptx
    pptx_bytes = generate_pptx(deck, image_loader=_image_loader)

    filename = doc.title.rsplit(".", 1)[0] if "." in doc.title else doc.title
    return Response(
        content=pptx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f'attachment; filename="{filename}.pptx"'},
    )


@router.get("/documents/{document_id}/images/{image_id}")
def get_image(
    document_id: str,
    image_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")
    if str(doc.owner_id) != current_user.user_id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    doc_img = (
        db.query(DocumentImage)
        .filter(DocumentImage.id == image_id, DocumentImage.document_id == document_id)
        .first()
    )
    if not doc_img:
        raise HTTPException(status_code=404, detail="IMAGE_NOT_FOUND")

    try:
        data = read_file_bytes(doc_img.storage_key)
    except StorageError as exc:
        raise HTTPException(status_code=503, detail=f"STORAGE_ERROR: {exc}") from exc

    ext = doc_img.storage_key.rsplit(".", 1)[-1] if "." in doc_img.storage_key else "png"
    media_type = f"image/{ext}" if ext != "jpg" else "image/jpeg"

    return Response(content=data, media_type=media_type)
