import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class JobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    failed = "failed"
    done = "done"


class DocumentStatus(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    ready = "ready"
    failed = "failed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    auth0_sub: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    documents: Mapped[list["Document"]] = relationship(back_populates="owner")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(500))
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    pages: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), default=DocumentStatus.uploaded)
    file_key: Mapped[str] = mapped_column(String(1024))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner: Mapped[User] = relationship(back_populates="documents")
    jobs: Mapped[list["Job"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    sections: Mapped[list["DeckSection"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    images: Mapped[list["DocumentImage"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), index=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.queued)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    document: Mapped[Document] = relationship(back_populates="jobs")


class SourceSpan(Base):
    __tablename__ = "source_spans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), index=True)
    page: Mapped[int] = mapped_column(Integer)
    paragraph_index: Mapped[int] = mapped_column(Integer)
    quote_snippet: Mapped[str] = mapped_column(Text)
    char_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    char_end: Mapped[int | None] = mapped_column(Integer, nullable=True)


class DocumentImage(Base):
    __tablename__ = "document_images"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), index=True)
    page: Mapped[int] = mapped_column(Integer)
    image_index: Mapped[int] = mapped_column(Integer)
    storage_key: Mapped[str] = mapped_column(String(1024))
    width: Mapped[int] = mapped_column(Integer)
    height: Mapped[int] = mapped_column(Integer)
    is_formula: Mapped[bool] = mapped_column(Boolean, default=False)
    latex: Mapped[str | None] = mapped_column(Text, nullable=True)

    document: Mapped[Document] = relationship(back_populates="images")


class DeckSection(Base):
    __tablename__ = "deck_sections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), index=True)
    heading: Mapped[str] = mapped_column(String(500))
    summary_note: Mapped[str] = mapped_column(Text, default="")
    sort_index: Mapped[int] = mapped_column(Integer, default=0)

    document: Mapped[Document] = relationship(back_populates="sections")
    subsections: Mapped[list["DeckSubsection"]] = relationship(back_populates="section", cascade="all, delete-orphan")


class DeckSubsection(Base):
    __tablename__ = "deck_subsections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    section_id: Mapped[str] = mapped_column(String(36), ForeignKey("deck_sections.id"), index=True)
    heading: Mapped[str] = mapped_column(String(500))
    annotation: Mapped[str] = mapped_column(Text, default="")
    sort_index: Mapped[int] = mapped_column(Integer, default=0)

    section: Mapped[DeckSection] = relationship(back_populates="subsections")
    bullets: Mapped[list["DeckBullet"]] = relationship(back_populates="subsection", cascade="all, delete-orphan")


class DeckBullet(Base):
    __tablename__ = "deck_bullets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    subsection_id: Mapped[str] = mapped_column(String(36), ForeignKey("deck_subsections.id"), index=True)
    text: Mapped[str] = mapped_column(Text)
    sort_index: Mapped[int] = mapped_column(Integer, default=0)
    image_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("document_images.id"), nullable=True)

    subsection: Mapped[DeckSubsection] = relationship(back_populates="bullets")
    citations: Mapped[list["BulletCitation"]] = relationship(back_populates="bullet", cascade="all, delete-orphan")
    image: Mapped["DocumentImage | None"] = relationship()


class BulletCitation(Base):
    __tablename__ = "bullet_citations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    bullet_id: Mapped[str] = mapped_column(String(36), ForeignKey("deck_bullets.id"), index=True)
    source_span_id: Mapped[str] = mapped_column(String(36), ForeignKey("source_spans.id"), index=True)

    bullet: Mapped[DeckBullet] = relationship(back_populates="citations")
