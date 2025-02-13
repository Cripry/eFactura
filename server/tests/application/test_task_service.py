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
from domain.task.task import TaskStatus, Task


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


def test_create_and_get_task_status(task_service, mock_repository, test_company):
    # Arrange
    from domain.task.schemas import TaskRequest

    task_data = TaskRequest(IDNO="123", seria="A", number=1)

    # Mock repository responses
    mock_repository.task_exists.return_value = False
    mock_repository.save_tasks.return_value = None
    mock_repository.get_tasks_status.return_value = [
        {"IDNO": "123", "seria": "A", "number": 1, "status": "WAITING"}
    ]

    # Act
    # Create task
    task_service.create_tasks(test_company.company_uuid, [task_data])

    # Get task status
    status = task_service.get_tasks_status(test_company.company_uuid, [task_data])

    # Assert
    assert len(status) == 1
    assert status[0]["status"] == "WAITING"


def test_get_waiting_tasks_for_machine(task_service, mock_repository, test_company):
    # Arrange
    from domain.task.schemas import TaskRequest

    task_data = TaskRequest(IDNO="123", seria="A", number=1)

    # Mock repository responses
    mock_repository.task_exists.return_value = False
    mock_repository.save_tasks.return_value = None
    mock_repository.get_waiting_tasks_by_company.return_value = [
        Task(task_uuid=uuid4(), IDNO="123", seria="A", number=1)
    ]

    # Act
    # Create task
    task_service.create_tasks(test_company.company_uuid, [task_data])

    # Get waiting tasks
    waiting_tasks = task_service.get_waiting_tasks_for_machine(
        test_company.company_uuid
    )

    # Assert
    assert "123" in waiting_tasks
    assert len(waiting_tasks["123"]) == 1
    assert waiting_tasks["123"][0]["seria_char"] == "A"
    assert waiting_tasks["123"][0]["seria_number"] == "1"


def test_update_and_verify_task_status(task_service, mock_repository, test_company):
    # Arrange
    from domain.task.schemas import TaskRequest

    task_data = TaskRequest(IDNO="123", seria="A", number=1)
    new_status = "COMPLETED"

    # Mock repository responses
    mock_repository.task_exists.return_value = False
    mock_repository.save_tasks.return_value = None
    mock_repository.update_tasks_status.return_value = 1
    mock_repository.get_tasks_status.return_value = [
        {"IDNO": "123", "seria": "A", "number": 1, "status": new_status}
    ]

    # Act
    # Create task
    task_service.create_tasks(test_company.company_uuid, [task_data])

    # Update task status
    task_service.update_tasks_status(test_company.company_uuid, [task_data], new_status)

    # Get task status
    status = task_service.get_tasks_status(test_company.company_uuid, [task_data])

    # Assert
    assert status[0]["status"] == new_status
