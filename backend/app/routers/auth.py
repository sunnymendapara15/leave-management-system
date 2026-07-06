from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from app.core.security import verify_password, create_access_token
from app.database import get_session
from app.models import User
from app.schemas import AuthRequest, AuthResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=AuthResponse)
def login(data: AuthRequest, session: Session = Depends(get_session)):
    query = select(User)
    if data.employee_id:
        query = query.where(User.employee_id == data.employee_id)
    elif data.email:
        query = query.where(User.email == data.email)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide email or employee ID along with password.",
        )
    user = session.exec(query).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = create_access_token(
        data={
            "user_id": user.id,
            "email": user.email,
            "employee_id": user.employee_id,
            "role": user.role.value,
        },
        expires_delta=timedelta(minutes=90),
    )
    return AuthResponse(
        access_token=access_token,
        user_id=user.id,
        expiry=datetime.utcnow() + timedelta(minutes=90),
    )
