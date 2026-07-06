from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlmodel import Session

from app.core.policies import LEAVE_TYPES
from app.core.security import get_password_hash
from app.database import get_session
from app.models import AuditLog, LeaveBalance, LeaveRequest, LeaveStatus, Team, User
from app.schemas import DummyDataResponse, LeaveRequestRead, UserRead

router = APIRouter(prefix="/api/dummy", tags=["dummy"])


@router.post("/seed", response_model=DummyDataResponse)
def seed_data(session: Session = Depends(get_session)):
    existing = session.exec(select(User)).first()
    if existing:
        return DummyDataResponse(
            users=[
                UserRead(
                    id=u.id,
                    employee_id=u.employee_id,
                    name=u.name,
                    email=u.email,
                    role=u.role.value,
                    manager_id=u.manager_id,
                    team_id=u.team_id,
                )
                for u in session.exec(select(User)).all()
            ],
            leave_types=list(LEAVE_TYPES.keys()),
            sample_requests=[],
        )

    team_alpha = Team(name="Alpha", description="Product Delivery")
    team_beta = Team(name="Beta", description="Operations")
    session.add(team_alpha)
    session.add(team_beta)
    session.commit()
    session.refresh(team_alpha)
    session.refresh(team_beta)

    manager = User(
        employee_id="MNG-001",
        name="Jordan Lee",
        email="jordan@example.com",
        role="manager",
        hashed_password=get_password_hash("manager123"),
        team_id=team_alpha.id,
    )
    employee = User(
        employee_id="EMP-101",
        name="Riya Shah",
        email="riya@example.com",
        role="employee",
        manager_id=None,
        hashed_password=get_password_hash("employee123"),
        team_id=team_alpha.id,
    )
    hr = User(
        employee_id="HR-001",
        name="Tomas Chen",
        email="tomas@example.com",
        role="hr",
        hashed_password=get_password_hash("hrpass"),
        team_id=team_beta.id,
    )
    session.add_all([manager, employee, hr])
    session.commit()
    session.refresh(manager)
    session.refresh(employee)
    session.refresh(hr)

    balances = []
    for user in [manager, employee, hr]:
        for code, meta in LEAVE_TYPES.items():
            balances.append(
                LeaveBalance(
                    user_id=user.id,
                    leave_type_code=code,
                    allocated=meta["yearly_quota"],
                    used=0,
                )
            )
    session.add_all(balances)

    sample_leave = LeaveRequest(
        user_id=employee.id,
        leave_type_code="AL",
        start_date=date(2026, 7, 20),
        end_date=date(2026, 7, 24),
        days=5,
        reason="Family trip",
        status=LeaveStatus.approved,
        approved_by=manager.id,
    )
    session.add(sample_leave)
    session.add(
        AuditLog(
            user_id=employee.id,
            action="dummy_seed",
            detail="Seeded baseline users and leave data",
        )
    )
    session.commit()

    users = session.exec(select(User)).all()
    requests = session.exec(select(LeaveRequest)).all()
    return DummyDataResponse(
        users=[
            UserRead(
                id=u.id,
                employee_id=u.employee_id,
                name=u.name,
                email=u.email,
                role=u.role.value,
                manager_id=u.manager_id,
                team_id=u.team_id,
            )
            for u in users
        ],
        leave_types=list(LEAVE_TYPES.keys()),
        sample_requests=[
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
            for r in requests
        ],
    )
