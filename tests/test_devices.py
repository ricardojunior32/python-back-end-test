import pytest
from fastapi import status
from app.devices.sensor_enum import SensorTypeEnum


def test_create_device(authenticated_client, test_client):
    """Testa criação de dispositivo"""
    payload = {
        "name": "Sensor TCAG - Test",
        "client_id": test_client.id,
        "sensor_type": "tcag"
    }
    
    response = authenticated_client.post("/devices/", json=payload)
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Sensor TCAG - Test"
    assert data["sensor_type"] == "tcag"
    assert "uid" in data
    assert "id" in data


def test_get_device_by_id(authenticated_client, test_device):
    """Testa busca de dispositivo por ID"""
    response = authenticated_client.get(f"/devices/{test_device.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_device.id
    assert data["uid"] == test_device.uid
    assert data["name"] == test_device.name


def test_get_device_not_found(authenticated_client):
    """Testa busca de dispositivo inexistente"""
    response = authenticated_client.get("/devices/99999")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    detail = response.json()["detail"]
    assert "not found" in detail.lower() or "Not Found" in detail


def test_get_devices_by_client(authenticated_client, test_device, test_client):
    """Testa busca de dispositivos por cliente"""
    response = authenticated_client.get(f"/devices/{test_client.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(device["client_id"] == test_client.id for device in data)


def test_create_device_unauthorized(client, test_client):
    """Testa criação de dispositivo sem autenticação"""
    payload = {
        "name": "Sensor Test",
        "client_id": test_client.id,
        "sensor_type": "tcag"
    }
    
    response = client.post("/devices/", json=payload)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

