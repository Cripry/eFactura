import datetime
from uuid import uuid4
from infrastructure.persistence.sqlalchemy_task_repository import (
    SQLAlchemyTaskRepository,
)
from domain.task.task import Task
from domain.task.models import TaskModel
from domain.company.models import CompanyModel
from domain.exceptions import DatabaseException
import pytest


def test_save_tasks(db_session):
    # Arrange
    repository = SQLAlchemyTaskRepository(db_session)

    # Create a test company first
    company_uuid = uuid4()
    auth_token = str(uuid4())
    company = CompanyModel(
        company_uuid=company_uuid,
        name="Test Company",
        auth_token=auth_token,
        created_at=datetime.datetime.now(),
    )
    db_session.add(company)
    db_session.flush()

    tasks = [Task(task_uuid=uuid4(), my_company_idno="123", seria="A", number=1)]

    # Act
    repository.save_tasks(company_uuid, tasks)

    # Assert
    saved_task = db_session.query(TaskModel).first()
    assert saved_task is not None
    assert saved_task.my_company_idno == "123"


def test_save_tasks_integrity_error(db_session):
    # Arrange
    repository = SQLAlchemyTaskRepository(db_session)
    company_uuid = uuid4()
    company = CompanyModel(
        company_uuid=company_uuid,
        name="Test Company",
        auth_token=str(uuid4()),
        created_at=datetime.datetime.now(),
    )
    db_session.add(company)
    db_session.flush()

    # Create duplicate tasks
    tasks = [
        Task(task_uuid=uuid4(), my_company_idno="123", seria="A", number=1),
        Task(task_uuid=uuid4(), my_company_idno="123", seria="A", number=1),
    ]

    # Act & Assert
    with pytest.raises(DatabaseException):
        repository.save_tasks(company_uuid, tasks)
