# Backend - Leave Management API

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Endpoints
| Path | Method | Purpose |
| --- | --- | --- |
| `/api/dummy/seed` | POST | Seed demo users, balances, requests. |
| `/api/auth/login` | POST | Authenticate by employee ID/email + password. |
| `/api/leaves/balances/{employee_id}` | GET | Retrieve leave balances. |
| `/api/leaves/requests/{employee_id}` | GET | List leave history for employee. |
| `/api/leaves/requests/{employee_id}` | POST | Apply for leave. |
| `/api/leaves/requests/{request_id}/action` | POST | Manager approve/reject request. |
| `/api/reports/summary/{employee_id}` | GET | Activity summary and upcoming leaves. |

## Policies enforced
- Advance notice of 7 days for planned leaves (AL, CL, etc.).
- Sick leaves longer than 3 days require medical certificates.
- Balance checks to prevent drops below zero (except LWP).
- Team overlap limits (<=3 per window).
