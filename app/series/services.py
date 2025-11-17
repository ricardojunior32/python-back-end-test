from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from app.series.models import TimeSeries
from app.series.schemas import TimeSeriesCreate
from fastapi import HTTPException
import statistics

def create_series(db: Session, payload: TimeSeriesCreate):
    new_series = TimeSeries(
        name=payload.name,
        values=payload.values
    )
    db.add(new_series)
    db.commit()
    db.refresh(new_series)
    return new_series

def delete_series(db: Session, series_id: int, deleted_by: str  = "system"):
    series = db.query(TimeSeries).filter(TimeSeries.id == series_id).first()
    if not series:
        raise HTTPException(status_code=404, detail="Error deleting series: Series not found!")
    series.is_active = False
    series.deleted_at = func.now()
    series.deleted_by = "system"

def get_series(db: Session, series_id: int):
    return db.query(TimeSeries).filter(TimeSeries.id == series_id).first()

def count_series(db: Session):
    return db.query(TimeSeries).count()

def get_metrics(values: list[float]):
    return {
        "mean": statistics.mean(values),
        "min": min(values),
        "max": max(values),
        "std": statistics.pstdev(values),
        "count": len(values)
    }
