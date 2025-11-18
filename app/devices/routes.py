from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.devices.schemas import DeviceCreate, DeviceResponse, DevicesResponse
from app.devices.services import create_device, get_devices, get_device
from app.core.auth import get_current_user

router = APIRouter(prefix="/devices", tags=["Devices"], dependencies=[Depends(get_current_user)])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DeviceResponse)
def create(payload: DeviceCreate, db: Session = Depends(get_db)):
    return create_device(db, payload)

@router.get("/{client_id}", response_model=list[DevicesResponse])
def get_devices_route(client_id: str, db: Session = Depends(get_db)):
    return get_devices(db, client_id)

@router.get("/{device_id}", response_model=DeviceResponse)
def get_device_route(device_id: int, db: Session = Depends(get_db)):
    device = get_device(db, device_id)
    if not device:
        raise HTTPException(404, "Device not found")
    return device
