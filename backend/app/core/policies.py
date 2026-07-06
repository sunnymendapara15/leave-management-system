from datetime import date

LEAVE_TYPES = {
    "AL": {
        "name": "Annual Leave",
        "yearly_quota": 20,
        "accrues_monthly": True,
        "carry_forward": 30,
        "requires_medical": False,
    },
    "SL": {
        "name": "Sick Leave",
        "yearly_quota": 10,
        "accrues_monthly": False,
        "carry_forward": 0,
        "requires_medical": True,
    },
    "CL": {
        "name": "Casual Leave",
        "yearly_quota": 7,
        "accrues_monthly": False,
        "carry_forward": 0,
        "requires_medical": False,
    },
    "MAT": {
        "name": "Maternity Leave",
        "yearly_quota": 26 * 5,  # treat as 130 days
        "accrues_monthly": False,
        "carry_forward": 0,
        "requires_medical": True,
    },
    "PAT": {
        "name": "Paternity Leave",
        "yearly_quota": 10,
        "accrues_monthly": False,
        "carry_forward": 0,
        "requires_medical": True,
    },
    "BRV": {
        "name": "Bereavement Leave",
        "yearly_quota": 5,
        "accrues_monthly": False,
        "carry_forward": 0,
        "requires_medical": False,
    },
    "LWP": {
        "name": "Leave Without Pay",
        "yearly_quota": 365,
        "accrues_monthly": False,
        "carry_forward": 0,
        "requires_medical": False,
    },
    "WFH": {
        "name": "Work From Home",
        "yearly_quota": 60,
        "accrues_monthly": False,
        "carry_forward": 0,
        "requires_medical": False,
    },
}

ADVANCE_NOTICE_DAYS = 7
MAX_TEAM_LEAVES = 3
COMPANY_RESET_MONTH = 1  # January


def count_days(start_date: date, end_date: date) -> int:
    delta = end_date - start_date
    return delta.days + 1
