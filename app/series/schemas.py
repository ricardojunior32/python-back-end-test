from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TimeSeriesCreate(BaseModel):
    name: str
    values: List[float]

class TimeSeriesResponse(BaseModel):
    id: int
    is_active: bool
    name: str
    values: List[float]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[str] = None

    class Config:
        orm_mode = True

class MessageResponse(BaseModel):
    message: str
    status: bool