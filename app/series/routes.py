from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.series.models import TimeSeries
from app.series.schemas import TimeSeriesCreate, TimeSeriesResponse, MessageResponse
from app.series.services import (create_series, delete_series, get_series, count_series, get_metrics) 

router = APIRouter(prefix="/series", tags=["timeseries"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TimeSeriesResponse ) 
def create_series(payload: TimeSeriesCreate, db: Session = Depends(get_db)):
    new_series = TimeSeries(
        name=payload.name,
        values=payload.values
    )
    db.add(new_series) 
    db.commit()
    db.refresh(new_series)
    return new_series

@router.delete("/{series_id}", response_model=MessageResponse)
def delete_series_route(series_id: int, db: Session = Depends(get_db), deleted_by: str = "system"):
    success = delete_series(db, series_id)
    print("Success", success)
    if not success:
        raise HTTPException(status_code=400, detail="Series not found")
    return MessageResponse(
        message="Series deleted successfully",
        status=True
    )

@router.get("/{series_id}", response_model=TimeSeriesResponse)
def get_series(series_id: int, db: Session = Depends(get_db)):
    return db.query(TimeSeries).filter(TimeSeries.id == series_id,).first()

