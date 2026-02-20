from pydantic import BaseModel


class CitationOut(BaseModel):
    page: int
    paragraph_index: int
    quote_snippet: str


class BulletOut(BaseModel):
    id: str
    text: str
    citations: list[CitationOut]
    image_url: str | None = None
    latex: str | None = None


class SubsectionOut(BaseModel):
    id: str
    heading: str
    annotation: str
    bullets: list[BulletOut]


class SectionOut(BaseModel):
    id: str
    heading: str
    summary_note: str
    subsections: list[SubsectionOut]


class QualityReport(BaseModel):
    coverage_ratio: float
    citation_completeness: float
    dedupe_ratio: float


class DeckOut(BaseModel):
    document_id: str
    title: str
    language: str | None
    quality_report: QualityReport
    sections: list[SectionOut]
