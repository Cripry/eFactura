from domain.task.task import Task
import uuid


def test_task_creation():
    # Arrange
    task_uuid = uuid.uuid4()
    idno = "123"
    seria = "A"
    number = 1

    # Act
    task = Task(task_uuid=task_uuid, idno=idno, seria=seria, number=number)

    # Assert
    assert task.task_uuid == task_uuid
    assert task.idno == idno
    assert task.seria == seria
    assert task.number == number
