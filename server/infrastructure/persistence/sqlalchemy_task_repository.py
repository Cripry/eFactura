from domain.task.repository import TaskRepository
from domain.task.task import Task, CompanyTask, TaskStatus
from domain.task.models import TaskModel, CompanyTaskModel
from sqlalchemy import exc
from domain.exceptions import DatabaseException
import uuid
from typing import List


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session):
        self.session = session

    def task_exists(self, idno: str, seria: str, number: int) -> bool:
        return bool(
            self.session.query(TaskModel)
            .filter_by(idno=idno, seria=seria, number=number)
            .first()
        )

    def save_tasks(self, company_uuid: uuid.UUID, tasks: List[Task]) -> None:
        try:
            # Create individual tasks
            for task in tasks:
                task_model = TaskModel(
                    task_uuid=uuid.uuid4(),
                    idno=task.IDNO,
                    seria=task.seria,
                    number=task.number,
                )
                self.session.add(task_model)
                self.session.flush()

                # Create company task
                company_task = CompanyTaskModel(
                    task_uuid=task_model.task_uuid,
                    company_uuid=company_uuid,
                    status=TaskStatus.WAITING.value,
                )
                self.session.add(company_task)

            self.session.commit()

        except exc.IntegrityError as e:
            self.session.rollback()
            raise DatabaseException("Database integrity error", str(e.orig))
        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to save tasks", str(e))

    def find_tasks_by_company(self, company_uuid: uuid.UUID) -> List[CompanyTask]:
        return (
            self.session.query(CompanyTaskModel)
            .filter_by(company_uuid=company_uuid)
            .all()
        )

    def get_tasks_status(
        self, company_uuid: uuid.UUID, tasks: List[Task]
    ) -> List[dict]:
        results = []
        for task in tasks:
            company_task = (
                self.session.query(CompanyTaskModel)
                .join(TaskModel)
                .filter(
                    TaskModel.idno == task.IDNO,
                    TaskModel.seria == task.seria,
                    TaskModel.number == task.number,
                    CompanyTaskModel.company_uuid == company_uuid,
                )
                .first()
            )

            if company_task:
                results.append(
                    {
                        "IDNO": task.IDNO,
                        "seria": task.seria,
                        "number": task.number,
                        "status": company_task.status,
                    }
                )
            else:
                results.append(
                    {
                        "IDNO": task.IDNO,
                        "seria": task.seria,
                        "number": task.number,
                        "status": "not_found",
                    }
                )
        return results

    def get_waiting_tasks_by_company(self, company_uuid: uuid.UUID) -> List[Task]:
        tasks = (
            self.session.query(TaskModel)
            .join(CompanyTaskModel)
            .filter(
                CompanyTaskModel.company_uuid == company_uuid,
                CompanyTaskModel.status == TaskStatus.WAITING.value,
            )
            .all()
        )
        return [
            Task(
                task_uuid=task.task_uuid,
                IDNO=task.idno,
                seria=task.seria,
                number=task.number,
            )
            for task in tasks
        ]

    def update_tasks_status(
        self, company_uuid: uuid.UUID, tasks: List[Task], new_status: str
    ) -> int:
        try:
            updated_count = 0
            for task in tasks:
                # Find the company task to update
                company_task = (
                    self.session.query(CompanyTaskModel)
                    .join(TaskModel)
                    .filter(
                        TaskModel.idno == task.IDNO,
                        TaskModel.seria == task.seria,
                        TaskModel.number == task.number,
                        CompanyTaskModel.company_uuid == company_uuid,
                    )
                    .first()
                )

                if company_task:
                    company_task.status = new_status
                    updated_count += 1

            self.session.commit()
            return updated_count
        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Database error while updating tasks", str(e))

    def task_belongs_to_company(
        self, company_uuid: uuid.UUID, idno: str, seria: str, number: int
    ) -> bool:
        return bool(
            self.session.query(CompanyTaskModel)
            .join(TaskModel)
            .filter(
                TaskModel.idno == idno,
                TaskModel.seria == seria,
                TaskModel.number == number,
                CompanyTaskModel.company_uuid == company_uuid,
            )
            .first()
        )
