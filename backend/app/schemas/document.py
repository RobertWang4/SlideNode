from pydantic import BaseModel


class DocumentCreateOut(BaseModel):
    document_id: str
    job_id: str


class DocumentListItem(BaseModel):
    id: str
    title: str
    status: str
    pages: int | None
    created_at: str


class DocumentListOut(BaseModel):
    items: list[DocumentListItem]
    total: int
