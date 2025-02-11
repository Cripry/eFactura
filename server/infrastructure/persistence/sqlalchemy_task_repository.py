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

    def save_tasks(self, company_uuid: uuid.UUID, tasks: List[Task]) -> CompanyTask:
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
            return company_task
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
