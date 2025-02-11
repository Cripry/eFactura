from domain.task.task import Task
from domain.task.repository import TaskRepository
from typing import List, Dict, Any
from fastapi import HTTPException, status
import uuid


class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def create_tasks(
        self, company_uuid: uuid.UUID, task_data: List[dict]
    ) -> Dict[str, Any]:
        try:
            tasks = [
                Task(
                    task_uuid=uuid.uuid4(),
                    IDNO=task.IDNO,
                    seria=task.seria,
                    number=task.number,
                )
                for task in task_data
            ]

            company_task = self.task_repository.save_tasks(company_uuid, tasks)
            return {
                "message": "All tasks created successfully",
                "task_uuid": str(company_task.task_uuid),
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Failed to create tasks", "details": str(e)},
            )
