import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from domain.task.models import Base as TaskBase
from domain.company.models import Base as CompanyBase, CompanyModel
from uuid import uuid4
import datetime


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Create a temporary database file for testing"""
    return str(tmp_path_factory.mktemp("data") / "test.db")


@pytest.fixture(scope="session")
def engine(test_db_path):
    """Create engine with physical SQLite database"""
    engine = create_engine(f"sqlite:///{test_db_path}")
    # Create all tables
    TaskBase.metadata.create_all(engine)
    CompanyBase.metadata.create_all(engine)
    yield engine

    # Ensure all connections are closed
    engine.dispose()

    # Drop all tables
    TaskBase.metadata.drop_all(engine)
    CompanyBase.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
        engine.dispose()  # Ensure engine is disposed


@pytest.fixture
def test_company(db_session):
    """Create and return a test company"""
    company = CompanyModel(
        company_uuid=uuid4(),
        name="Test Company_" + str(uuid4()),
        auth_token=str(uuid4()),
        created_at=datetime.datetime.now(),
    )
    db_session.add(company)
    db_session.flush()
    return company


@pytest.fixture
def test_task_data():
    """Return sample task data"""
    return [{"IDNO": "123", "seria": "A", "number": 1}]
