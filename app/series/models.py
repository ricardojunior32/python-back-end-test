from sqlalchemy import Column, Integer, String, JSON, Boolean, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class TimeSeries(Base):
    __tablename__ = "time_series"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    values = Column(JSON, nullable=False)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(String, nullable=True)
