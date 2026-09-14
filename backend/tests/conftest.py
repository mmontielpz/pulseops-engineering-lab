from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def _make_test_engine():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_engine(
        f"sqlite:///{path}", connect_args={"check_same_thread": False}
    )
    return engine, path


@pytest.fixture()
def db_session() -> Iterator[Session]:
    """A fresh SQLite file per test, so tests never share state."""
    from app.db import Base

    engine, path = _make_test_engine()
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        os.remove(path)


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """A TestClient whose get_db dependency points at an isolated SQLite file."""
    from app.db import Base, get_db
    from app.main import app

    engine, path = _make_test_engine()
    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(bind=engine)

    def override_get_db() -> Iterator[Session]:
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        os.remove(path)
