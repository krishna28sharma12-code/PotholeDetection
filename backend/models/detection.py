from pydantic import BaseModel
from typing import Optional

class UploadResponse(BaseModel):
    detected: bool
    id: Optional[int] = None
    severity: Optional[str] = None
    confidence: Optional[float] = None
