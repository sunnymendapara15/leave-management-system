from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import auth, dummy, leave_requests, reports

app = FastAPI(
    title="Leave Management System",
    description="Policy-aware LMS supporting leave balances, approvals, and dummy data utilities.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(leave_requests.router)
app.include_router(reports.router)
app.include_router(dummy.router)


@app.on_event("startup")
def startup_event():
    init_db()
