from domain.task.task import Task
from domain.task.repository import TaskRepository
from typing import List, Dict, Any, Set, Tuple
from fastapi import HTTPException, status
import uuid


class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def _get_existing_tasks(self, tasks: List[Task]) -> Set[Tuple[str, str, int]]:
        """Check if any of the tasks already exist in the database"""
        existing_tasks = set()
        for task in tasks:
            if self.task_repository.task_exists(task.IDNO, task.seria, task.number):
                existing_tasks.add((task.IDNO, task.seria, task.number))
        return existing_tasks

    def _check_for_duplicates(self, task_data: List[dict]) -> List[dict]:
        """Check for duplicates within the provided task data"""
        seen = set()
        duplicates = []
        for task in task_data:
            task_key = (task.IDNO, task.seria, task.number)
            if task_key in seen:
                duplicates.append(task)
            else:
                seen.add(task_key)
        return duplicates

    def create_tasks(
        self, company_uuid: uuid.UUID, task_data: List[dict]
    ) -> Dict[str, Any]:
        try:
            # First check for duplicates within the provided data
            duplicates = self._check_for_duplicates(task_data)
            if duplicates:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "message": "Duplicate tasks found in the request",
                        "duplicates": duplicates,
                    },
                )

            # Convert to Task objects
            tasks = [
                Task(
                    task_uuid=uuid.uuid4(),
                    IDNO=task.IDNO,
                    seria=task.seria,
                    number=task.number,
                )
                for task in task_data
            ]

            # Check for existing tasks in the database
            existing_tasks = self._get_existing_tasks(tasks)
            if existing_tasks:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "message": "Some tasks already exist in the database",
                        "existing_tasks": [
                            {"IDNO": t[0], "seria": t[1], "number": t[2]}
                            for t in existing_tasks
                        ],
                    },
                )

            # If no duplicates, proceed with creation
            self.task_repository.save_tasks(company_uuid, tasks)
            return {"message": "All tasks created successfully"}

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Failed to create tasks", "details": str(e)},
            )

    def get_tasks_status(
        self, company_uuid: uuid.UUID, task_data: List[dict]
    ) -> List[dict]:
        """Get status of tasks for a company"""
        try:
            # Convert to Task objects
            tasks = [
                Task(
                    task_uuid=uuid.uuid4(),  # Not used, just for object creation
                    IDNO=task.IDNO,
                    seria=task.seria,
                    number=task.number,
                )
                for task in task_data
            ]

            # Get statuses from repository
            return self.task_repository.get_tasks_status(company_uuid, tasks)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": "Failed to get tasks status", "details": str(e)},
            )
