from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlmodel import Session

from app.database import get_session
from app.models import LeaveRequest, LeaveStatus, User
from app.schemas import ReportSummary

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/summary/{employee_id}", response_model=ReportSummary)
def summary(employee_id: str, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.employee_id == employee_id)).first()
    today = date.today()
    stmt = select(LeaveRequest).where(LeaveRequest.user_id == user.id)
    requests = session.exec(stmt).all()
    upcoming = sum(1 for r in requests if r.start_date >= today and r.status == LeaveStatus.approved)
    approved = sum(1 for r in requests if r.status == LeaveStatus.approved)
    pending = sum(1 for r in requests if r.status == LeaveStatus.pending)
    rejected = sum(1 for r in requests if r.status == LeaveStatus.rejected)
    return ReportSummary(
        total_requests=len(requests),
        approved=approved,
        pending=pending,
        rejected=rejected,
        upcoming_leaves=upcoming,
    )
