def test_create_and_get_task_status(db_session, task_service, test_company):
    # Arrange
    from domain.task.schemas import TaskRequest

    task_data = TaskRequest(my_company_idno="123", seria="A", number=1)

    # Act
    # Create task
    create_result = task_service.create_tasks(test_company.company_uuid, [task_data])

    # Get task status
    status = task_service.get_tasks_status(test_company.company_uuid, [task_data])

    # Assert
    assert create_result["message"] == "All tasks created successfully"
    assert len(status) == 1
    assert status[0]["status"] == "WAITING"


def test_task_grouping_for_machine(db_session, task_service, test_company):
    # Arrange
    from domain.task.schemas import TaskRequest

    tasks_data = [
        TaskRequest(my_company_idno="123", seria="A", number=1),
        TaskRequest(my_company_idno="123", seria="B", number=2),
        TaskRequest(my_company_idno="456", seria="C", number=3),
    ]

    # Act
    # Create tasks
    task_service.create_tasks(test_company.company_uuid, tasks_data)

    # Get waiting tasks
    waiting_tasks = task_service.get_waiting_tasks_for_machine(
        test_company.company_uuid
    )

    # Assert
    assert "123" in waiting_tasks
    assert "456" in waiting_tasks
    assert len(waiting_tasks["123"]) == 2
    assert len(waiting_tasks["456"]) == 1


def test_task_status_update(db_session, task_service, test_company):
    # Arrange
    from domain.task.schemas import TaskRequest

    task_data = TaskRequest(my_company_idno="123", seria="A", number=1)
    new_status = "COMPLETED"

    # Act
    # Create task
    task_service.create_tasks(test_company.company_uuid, [task_data])

    # Update status
    update_result = task_service.update_tasks_status(
        test_company.company_uuid, [task_data], new_status
    )

    # Get status
    status = task_service.get_tasks_status(test_company.company_uuid, [task_data])

    # Assert
    assert update_result["message"] == "Successfully updated 1 tasks"
    assert status[0]["status"] == new_status
