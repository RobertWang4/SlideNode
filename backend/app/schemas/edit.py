from pydantic import BaseModel, Field


class PatchBullet(BaseModel):
    id: str
    text: str


class PatchSubsection(BaseModel):
    id: str
    heading: str | None = None
    annotation: str | None = None
    bullets: list[PatchBullet] = Field(default_factory=list)


class PatchSection(BaseModel):
    id: str
    heading: str | None = None
    summary_note: str | None = None
    subsections: list[PatchSubsection] = Field(default_factory=list)


class DeckPatchRequest(BaseModel):
    sections: list[PatchSection] = Field(default_factory=list)
