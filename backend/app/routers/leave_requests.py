from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlmodel import Session

from app.core.policies import LEAVE_TYPES
from app.database import get_session
from app.models import AuditLog, LeaveBalance, LeaveRequest, LeaveStatus, User
from app.schemas import BalanceItem, BalanceResponse, LeaveRequestAction, LeaveRequestCreate, LeaveRequestRead
from app.services.leave_service import calculate_days, validate_leave_request

router = APIRouter(prefix="/api/leaves", tags=["leaves"])


def get_user_by_employee(session: Session, employee_id: str) -> User:
    result = session.exec(select(User).where(User.employee_id == employee_id)).first()
    if not result:
        raise HTTPException(status_code=404, detail="Employee not found")
    return result


def get_balance_items(session: Session, user: User):
    balances = session.exec(select(LeaveBalance).where(LeaveBalance.user_id == user.id)).all()
    items = []
    for balance in balances:
        items.append(
            BalanceItem(
                leave_type_code=balance.leave_type_code,
                allocated=balance.allocated,
                used=balance.used,
                remaining=max(balance.allocated - balance.used, 0),
            )
        )
    return items


@router.get("/balances/{employee_id}", response_model=BalanceResponse)
def balances(employee_id: str, session: Session = Depends(get_session)):
    user = get_user_by_employee(session, employee_id)
    return BalanceResponse(employee_id=user.employee_id, balances=get_balance_items(session, user))


@router.post("/requests/{employee_id}", response_model=LeaveRequestRead)
def create_request(
    employee_id: str,
    payload: LeaveRequestCreate,
    session: Session = Depends(get_session),
):
    user = get_user_by_employee(session, employee_id)
    policy = LEAVE_TYPES.get(payload.leave_type_code)
    if not policy:
        raise HTTPException(status_code=400, detail="Unsupported leave type")
    error = validate_leave_request(
        session,
        user,
        payload.leave_type_code,
        payload.start_date,
        payload.end_date,
        payload.medical_certificate_submitted or False,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)
    days = calculate_days(payload.start_date, payload.end_date)
    leave = LeaveRequest(
        user_id=user.id,
        leave_type_code=payload.leave_type_code,
        start_date=payload.start_date,
        end_date=payload.end_date,
        days=days,
        reason=payload.reason,
        requires_medical=policy["requires_medical"],
        medical_certificate_submitted=payload.medical_certificate_submitted or False,
    )
    session.add(leave)
    session.add(
        AuditLog(
            user_id=user.id,
            action="leave_requested",
            detail=f"Requested {payload.leave_type_code} for {days} days",
        )
    )
    session.commit()
    session.refresh(leave)
    return LeaveRequestRead(
        id=leave.id,
        leave_type_code=leave.leave_type_code,
        start_date=leave.start_date,
        end_date=leave.end_date,
        days=leave.days,
        status=leave.status.value,
        reason=leave.reason,
        manager_notes=leave.manager_notes,
        requested_at=leave.requested_at,
    )


@router.get("/requests/{employee_id}", response_model=list[LeaveRequestRead])
def history(employee_id: str, session: Session = Depends(get_session)):
    user = get_user_by_employee(session, employee_id)
    stmt = select(LeaveRequest).where(LeaveRequest.user_id == user.id)
    results = session.exec(stmt).all()
    return [
        LeaveRequestRead(
            id=r.id,
            leave_type_code=r.leave_type_code,
            start_date=r.start_date,
            end_date=r.end_date,
            days=r.days,
            status=r.status.value,
            reason=r.reason,
            manager_notes=r.manager_notes,
            requested_at=r.requested_at,
        )
        for r in results
    ]


@router.post("/requests/{request_id}/action")
def take_action(
    request_id: int,
    payload: LeaveRequestAction,
    approver_id: Optional[int] = Query(None, description="Manager employee ID performing action"),
    session: Session = Depends(get_session),
):
    leave = session.exec(select(LeaveRequest).where(LeaveRequest.id == request_id)).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request missing")
    if leave.status != LeaveStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending requests can be actioned")
    leave.manager_notes = payload.notes
    leave.status = LeaveStatus.approved if payload.approved else LeaveStatus.rejected
    leave.approved_by = approver_id
    session.add(
        AuditLog(
            user_id=leave.user_id,
            action="leave_approved" if payload.approved else "leave_rejected",
            detail=f"{payload.notes or 'Decision recorded'}",
        )
    )
    if payload.approved:
        balance = session.exec(
            select(LeaveBalance).where(
                LeaveBalance.user_id == leave.user_id,
                LeaveBalance.leave_type_code == leave.leave_type_code,
            )
        ).first()
        if balance:
            balance.used += leave.days
            session.add(balance)
    session.add(leave)
    session.commit()
    session.refresh(leave)
    return {"status": leave.status.value, "manager_notes": leave.manager_notes}
