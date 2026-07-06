# Leave Management System

Policy-aware Leave Management System with a React frontend and FastAPI backend, enforcing advance notice, balance rules, medical certificate requirements, and offering dummy data utilities for demos.

## Stack
- **Frontend:** React (Create React App) with Axios for API calls.
- **Backend:** FastAPI + SQLModel (SQLite) for persistence, JWT-based auth utilities, and policy-centric routing.

## Setup
1. **Clone repository** *(already done)*
2. **Backend dependencies**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
3. **Frontend dependencies**
   ```bash
   cd frontend
   npm install
   npm start
   ```
   The React app proxies requests to `http://localhost:8000`.

## Key APIs
- `POST /api/dummy/seed`: seeds policy-aware dummy data.
- `POST /api/auth/login`: authenticate using employee ID/email + password.
- `GET /api/leaves/balances/{employee_id}`: fetch balance per leave type.
- `POST /api/leaves/requests/{employee_id}`: apply for leave.
- `POST /api/leaves/requests/{request_id}/action`: managers approve or reject requests.
- `GET /api/leaves/requests/{employee_id}`: review history.
- `GET /api/reports/summary/{employee_id}`: aggregated counts and upcoming leaves.

## Policies enforced
- Advance notice of 7 days for planned leaves (except sick leave).
- Sick leave >3 days mandates medical certificate.
- No approvals that drop balances below zero (LWP excluded).
- Team overlap limit (max 3 approvers per window).
- Audit logs capture all actions.

## Dummy data summary
- Two teams (Alpha, Beta), manager, HR, and employee sample users.
- Preloaded leave balances covering AL, SL, CL, Maternity/Paternity/Bereavement, LWP, WFH.
- Approved Annual Leave for the employee for July 20-24, 2026.
