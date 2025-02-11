from sqlalchemy.orm import Session
from domain.task.repository import TaskRepository
from domain.task.task import Task, CompanyTask, TaskStatus
from domain.task.models import TaskModel, CompanyTaskModel
from sqlalchemy import exc
from fastapi import HTTPException, status
import uuid
from typing import List


class SQLAlchemyTaskRepository(TaskRepository):
    def __init__(self, session: Session):
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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"message": "Database integrity error", "details": str(e.orig)},
            )

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
