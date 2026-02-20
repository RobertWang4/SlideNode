import re
import uuid
from dataclasses import dataclass

import pymupdf

from app.core.config import settings


@dataclass
class ParsedChunk:
    chunk_id: str
    page: int
    paragraph_index: int
    text: str
    char_start: int
    char_end: int


@dataclass
class ParsedImage:
    image_id: str
    page: int
    image_index: int
    image_bytes: bytes
    ext: str  # "png", "jpeg"
    width: int
    height: int
    bbox: tuple[float, float, float, float]


def _normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _split_paragraphs(page_text: str) -> list[str]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", page_text) if p.strip()]
    if paras:
        return paras
    lines = [ln.strip() for ln in page_text.splitlines() if ln.strip()]
    return lines


def _estimate_tokens(text: str) -> int:
    # Conservative token estimate without tokenizer dependency.
    words = len(text.split())
    return max(1, int(words * 1.3))


def _chunk_paragraphs(paragraphs: list[tuple[int, str]], chunk_size: int) -> list[tuple[int, str]]:
    chunks: list[tuple[int, str]] = []
    current_page = paragraphs[0][0]
    current_parts: list[str] = []
    current_tokens = 0

    for page, para in paragraphs:
        para_tokens = _estimate_tokens(para)

        if current_parts and current_tokens + para_tokens > chunk_size:
            chunks.append((current_page, "\n\n".join(current_parts)))
            current_parts = [para]
            current_tokens = para_tokens
            current_page = page
            continue

        if not current_parts:
            current_page = page
        current_parts.append(para)
        current_tokens += para_tokens

    if current_parts:
        chunks.append((current_page, "\n\n".join(current_parts)))

    return chunks


def _extract_images_from_page(doc: pymupdf.Document, page: pymupdf.Page, page_num: int) -> list[ParsedImage]:
    """Extract embedded images from a single PDF page."""
    images: list[ParsedImage] = []
    image_list = page.get_images(full=True)

    for img_idx, img_info in enumerate(image_list):
        xref = img_info[0]
        try:
            extracted = doc.extract_image(xref)
        except Exception:  # noqa: BLE001
            continue

        if not extracted or not extracted.get("image"):
            continue

        ext = extracted.get("ext", "png")
        if ext == "jpg":
            ext = "jpeg"

        width = extracted.get("width", 0)
        height = extracted.get("height", 0)

        # Skip very small images (likely decorative)
        if width < 20 or height < 20:
            continue

        # Try to find the image's bounding box on the page
        bbox = (0.0, 0.0, float(width), float(height))
        for img_rect in page.get_image_rects(xref):
            bbox = (img_rect.x0, img_rect.y0, img_rect.x1, img_rect.y1)
            break

        images.append(
            ParsedImage(
                image_id=str(uuid.uuid4()),
                page=page_num,
                image_index=img_idx,
                image_bytes=extracted["image"],
                ext=ext,
                width=width,
                height=height,
                bbox=bbox,
            )
        )

    return images


def parse_pdf_bytes(data: bytes) -> tuple[int, list[ParsedChunk], list[ParsedImage]]:
    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception as exc:  # noqa: BLE001
        raise ValueError("PARSE_FAILED: invalid pdf") from exc

    pages = len(doc)
    if pages == 0:
        raise ValueError("PARSE_FAILED: empty pdf")

    paragraph_rows: list[tuple[int, str]] = []
    all_images: list[ParsedImage] = []

    for idx in range(pages):
        page = doc[idx]
        page_num = idx + 1

        # Text extraction
        raw = page.get_text() or ""
        normalized = _normalize_text(raw)
        if normalized:
            for para in _split_paragraphs(normalized):
                paragraph_rows.append((page_num, para))

        # Image extraction
        page_images = _extract_images_from_page(doc, page, page_num)
        all_images.extend(page_images)

    doc.close()

    if not paragraph_rows:
        raise ValueError("PARSE_FAILED: no extractable text")

    chunk_rows = _chunk_paragraphs(paragraph_rows, settings.chunk_size_tokens)

    chunks: list[ParsedChunk] = []
    offset = 0
    for i, (page, text) in enumerate(chunk_rows, start=1):
        start = offset
        end = start + len(text)
        chunks.append(
            ParsedChunk(
                chunk_id=f"c_{i:04d}",
                page=page,
                paragraph_index=i,
                text=text,
                char_start=start,
                char_end=end,
            )
        )
        offset = end + 1

    return pages, chunks, all_images
