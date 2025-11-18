import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import hash_password
from app.core.database import Base, get_db
from app.users.models import User
from app.clients.models import Client
from app.devices.models import Device
from app.series.models import TimeSeries
from app.devices.sensor_enum import SensorTypeEnum
from main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Cria um banco de dados limpo para cada teste"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Cliente de teste do FastAPI com override do banco"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    """Cria um usuário de teste"""
    password = "testpassword123"
    hashed = hash_password(password)
    
    user = User(
        name="Test User",
        email="test@example.com",
        hashed_password=hashed
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    print(f"\n=== USER CREATED ===")
    print(f"Email: {user.email}")
    print(f"ID: {user.id}")
    print(f"====================\n")
    
    return user


@pytest.fixture
def auth_token(client, test_user, db):
    """Obtém um token de autenticação - DEVE usar o mesmo db"""
    # Verificar se o usuário existe no banco
    from app.users.models import User
    user_check = db.query(User).filter(User.email == "test@example.com").first()
    
    print(f"\n=== BEFORE LOGIN ===")
    print(f"User exists in DB: {user_check is not None}")
    if user_check:
        print(f"User ID: {user_check.id}")
        print(f"User Hash: {user_check.hashed_password[:50]}...")
    print(f"====================\n")
    
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    
    print(f"\n=== LOGIN RESPONSE ===")
    print(f"Status: {response.status_code}")
    print(f"Body: {response.json()}")
    print(f"======================\n")
    
    assert response.status_code == 200, f"Login falhou: {response.status_code} - {response.json()}"
    
    data = response.json()
    assert "access_token" in data, f"access_token não encontrado: {data}"
    
    return data["access_token"]


@pytest.fixture
def authenticated_client(client, auth_token):
    """Cliente autenticado com token"""
    client.headers = {"Authorization": f"Bearer {auth_token}"}
    return client


@pytest.fixture
def test_client(db):
    """Cria um cliente de teste"""
    from app.clients.models import Client
    
    client = Client(
        name="Test Client",
        email="client@example.com",
        document="12345678000190"
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@pytest.fixture
def test_get_devices_by_client(authenticated_client, test_device, test_client):
    """Testa listagem de dispositivos por cliente"""
    response = authenticated_client.get(f"/devices/client/{test_client.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.fixture
def test_device(db, test_client):
    """Cria um dispositivo de teste"""
    from app.devices.models import Device
    from app.devices.sensor_enum import SensorTypeEnum
    
    device = Device(
        uid="test-device-uid-123",
        name="Test Device",
        sensor_type=SensorTypeEnum.TCAG,
        client_id=test_client.id,
        sensor_capabilities={
            "sobreaquecimento": True,
            "vibracao_anormal": True
        }
    )
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


@pytest.fixture
def test_series(db, test_device):
    """Cria uma série temporal de teste"""
    from app.series.models import TimeSeries
    
    series = TimeSeries(
        device_uid=test_device.uid,
        values=[
            {
                "value": 1.5,
                "timestamp": "2024-01-15T10:30:00",
                "quality": "good",
                "unit": "g-force"
            },
            {
                "value": 2.0,
                "timestamp": "2024-01-15T10:31:00",
                "quality": "good",
                "unit": "g-force"
            },
            {
                "value": 2.3,
                "timestamp": "2024-01-15T10:32:00",
                "quality": "good",
                "unit": "g-force"
            }
        ]
    )
    db.add(series)
    db.commit()
    db.refresh(series)
    return series
