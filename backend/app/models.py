from datetime import date, datetime
from enum import Enum
from typing import Optional, List

from sqlmodel import Field, Relationship, SQLModel


class Role(str, Enum):
    employee = "employee"
    manager = "manager"
    hr = "hr"


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    employees: List["User"] = Relationship(back_populates="team")


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: str = Field(index=True, sa_column_kwargs={"unique": True})
    name: str
    email: str = Field(index=True, sa_column_kwargs={"unique": True})
    role: Role = Field(default=Role.employee)
    manager_id: Optional[int] = Field(default=None, foreign_key="user.id")
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    is_active: bool = Field(default=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    manager: Optional["User"] = Relationship(back_populates="direct_reports", sa_relationship_kwargs={"remote_side": "User.id"})
    direct_reports: List["User"] = Relationship(back_populates="manager")
    team: Optional[Team] = Relationship(back_populates="employees")
    leave_requests: List["LeaveRequest"] = Relationship(back_populates="user")


class LeaveType(SQLModel, table=True):
    code: str = Field(primary_key=True)
    name: str
    description: Optional[str] = None
    yearly_quota: float
    accrues_monthly: bool = Field(default=False)
    carry_forward: float = Field(default=0)
    requires_medical: bool = Field(default=False)


class LeaveBalance(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    leave_type_code: str = Field(foreign_key="leavetype.code")
    allocated: float
    used: float = Field(default=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    __table_args__ = ({"sqlite_autoincrement": True},)


class LeaveStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


class LeaveRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    leave_type_code: str = Field(foreign_key="leavetype.code")
    start_date: date
    end_date: date
    days: float
    reason: str
    status: LeaveStatus = Field(default=LeaveStatus.pending)
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    manager_notes: Optional[str] = None
    approved_by: Optional[int] = Field(default=None, foreign_key="user.id")
    requires_medical: bool = Field(default=False)
    medical_certificate_submitted: bool = Field(default=False)
    hr_escalation: bool = Field(default=False)

    user: Optional[User] = Relationship(back_populates="leave_requests")


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[int]
    action: str
    detail: str
