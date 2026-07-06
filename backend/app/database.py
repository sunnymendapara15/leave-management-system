from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///" + str(Path(__file__).resolve().parents[1] / "leave_management.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)


def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    SQLModel.metadata.create_all(engine)
