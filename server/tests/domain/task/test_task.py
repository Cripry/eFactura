from domain.task.task import Task
import uuid


def test_task_creation():
    # Arrange
    task_uuid = uuid.uuid4()
    my_company_idno = "123"
    seria = "A"
    number = 1

    # Act
    task = Task(
        task_uuid=task_uuid, my_company_idno=my_company_idno, seria=seria, number=number
    )

    # Assert
    assert task.task_uuid == task_uuid
    assert task.my_company_idno == my_company_idno
    assert task.seria == seria
    assert task.number == number
