from pydantic import BaseModel


class JobOut(BaseModel):
    id: str
    status: str
    progress: float
    error_code: str | None
    error_detail: str | None
