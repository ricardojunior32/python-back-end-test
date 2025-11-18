from sqlalchemy.orm import Session
from app.users.models import User
from app.users.schemas import UserLogin
from app.core.security import verify_password
from fastapi import HTTPException, status

def authenticate_user(db: Session, payload: UserLogin):
    user = get_user_by_email(db, payload.email)
    if not user:
        return None  # Retorna None para email não encontrado
    
    if not verify_password(payload.password, user.hashed_password):
        return None  # Retorna None para senha incorreta também (consistência)
    
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()