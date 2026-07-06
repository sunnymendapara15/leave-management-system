from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class AuthRequest(BaseModel):
    employee_id: Optional[str]
    email: Optional[EmailStr]
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    expiry: datetime


class UserRead(BaseModel):
    id: int
    employee_id: str
    name: str
    email: EmailStr
    role: str
    manager_id: Optional[int]
    team_id: Optional[int]


class LeaveRequestCreate(BaseModel):
    leave_type_code: str
    start_date: date
    end_date: date
    reason: str
    medical_certificate_submitted: Optional[bool] = False


class LeaveRequestAction(BaseModel):
    approved: bool
    notes: Optional[str]


class LeaveRequestUpdate(BaseModel):
    action: LeaveRequestAction


class LeaveRequestRead(BaseModel):
    id: int
    leave_type_code: str
    start_date: date
    end_date: date
    days: float
    status: str
    reason: str
    manager_notes: Optional[str]
    requested_at: datetime


class BalanceItem(BaseModel):
    leave_type_code: str
    allocated: float
    used: float
    remaining: float


class BalanceResponse(BaseModel):
    employee_id: str
    balances: List[BalanceItem]


class ReportSummary(BaseModel):
    total_requests: int
    approved: int
    pending: int
    rejected: int
    upcoming_leaves: int


class DummyDataResponse(BaseModel):
    users: List[UserRead]
    leave_types: List[str]
    sample_requests: List[LeaveRequestRead]
