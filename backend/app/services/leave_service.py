from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlmodel import Session

from app.core.policies import ADVANCE_NOTICE_DAYS, LEAVE_TYPES, MAX_TEAM_LEAVES
from app.models import LeaveBalance, LeaveRequest, LeaveStatus, Team, User


def calculate_days(start: date, end: date) -> float:
    delta = end - start
    return delta.days + 1


def overlaps(start_a: date, end_a: date, start_b: date, end_b: date) -> bool:
    return not (end_a < start_b or start_a > end_b)


def get_user_balance(session: Session, user_id: int):
    balances = session.exec(select(LeaveBalance).where(LeaveBalance.user_id == user_id)).all()
    return balances


def team_overlap_count(session: Session, team_id: Optional[int], start_date: date, end_date: date) -> int:
    if not team_id:
        return 0
    stmt = select(LeaveRequest).join(User).where(
        User.team_id == team_id,
        LeaveRequest.status == LeaveStatus.approved,
    )
    leaves = session.exec(stmt).all()
    return sum(1 for leave in leaves if overlaps(start_date, end_date, leave.start_date, leave.end_date))


def ensure_balance(session: Session, user_id: int, leave_type_code: str, days: float) -> bool:
    balance = session.exec(
        select(LeaveBalance).where(
            LeaveBalance.user_id == user_id, LeaveBalance.leave_type_code == leave_type_code
        )
    ).first()
    if not balance:
        return False
    remaining = balance.allocated - balance.used
    if leave_type_code == "LWP":
        return True
    return remaining >= days


def validate_leave_request(
    session: Session, user: User, leave_type_code: str, start_date: date, end_date: date, medical_doc: bool
) -> Optional[str]:
    policy = LEAVE_TYPES.get(leave_type_code)
    if not policy:
        return f"Unknown leave type: {leave_type_code}"

    today = date.today()
    if leave_type_code != "SL":
        notice_gap = (start_date - today).days
        if notice_gap < ADVANCE_NOTICE_DAYS:
            return f"Planned {policy['name']} requires at least {ADVANCE_NOTICE_DAYS} days advance notice."

    days = (end_date - start_date).days + 1
    if days <= 0:
        return "End date must not be before start date."

    if policy["requires_medical"] and days > 3 and not medical_doc:
        return f"Medical certificate required for {policy['name']} longer than 3 days."

    if not ensure_balance(session, user.id, leave_type_code, days):
        return "Insufficient leave balance for this request."

    overlap_count = team_overlap_count(session, user.team_id, start_date, end_date)
    if overlap_count >= MAX_TEAM_LEAVES:
        return "Team already has multiple approved leaves in that range; please coordinate with the manager."

    return None
