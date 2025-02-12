import pytest
from uuid import uuid4
from domain.exceptions import (
    TaskExistsException,
    InvalidStatusException,
    DatabaseException,
)
from application.task_service import TaskService
from unittest.mock import MagicMock
from domain.task.schemas import TaskRequest
from domain.task.task import TaskStatus


@pytest.fixture
def mock_repository():
    return MagicMock()


@pytest.fixture
def task_service(mock_repository):
    return TaskService(mock_repository)


def test_create_tasks_success(task_service, mock_repository, test_company):
    # Arrange
    task_data = [TaskRequest(IDNO="123", seria="A", number=1)]
    mock_repository.task_exists.return_value = False

    # Act
    result = task_service.create_tasks(test_company.company_uuid, task_data)

    # Assert
    assert result["message"] == "All tasks created successfully"
    mock_repository.save_tasks.assert_called_once()


def test_create_tasks_duplicate(task_service, mock_repository):

    company_uuid = uuid4()
    task_data = [TaskRequest(IDNO="123", seria="A", number=1)]

    # Mock the repository to return existing tasks
    mock_repository.task_exists.return_value = True
    mock_repository.get_existing_tasks.return_value = [("123", "A", 1)]

    # Act & Assert
    with pytest.raises(TaskExistsException) as exc_info:
        task_service.create_tasks(company_uuid, task_data)

    # Verify exception details
    assert "already exist in the database" in str(exc_info.value)
    assert exc_info.value.existing_tasks == [{"IDNO": "123", "seria": "A", "number": 1}]


def test_update_tasks_status_invalid_status(task_service, mock_repository):
    # Arrange
    company_uuid = uuid4()
    task_data = [{"IDNO": "123", "seria": "A", "number": 1}]
    invalid_status = "INVALID_STATUS"

    # Act & Assert
    with pytest.raises(InvalidStatusException):
        task_service.update_tasks_status(company_uuid, task_data, invalid_status)


def test_update_tasks_status_database_error(task_service, mock_repository):
    # Arrange
    from domain.task.schemas import TaskRequest

    company_uuid = uuid4()
    task_data = [TaskRequest(IDNO="123", seria="A", number=1)]
    mock_repository.update_tasks_status.side_effect = Exception("DB error")

    # Use a valid status from TaskStatus enum
    valid_status = TaskStatus.WAITING.value

    # Act & Assert
    with pytest.raises(DatabaseException):
        task_service.update_tasks_status(company_uuid, task_data, valid_status)
