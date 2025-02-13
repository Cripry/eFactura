from domain.task.task import Task
from domain.task.repository import TaskRepository
from domain.task.schemas import TaskRequest, TaskStatusUpdateRequest
from typing import List, Dict, Any, Set, Tuple
from domain.exceptions import (
    DuplicateTaskException,
    TaskExistsException,
    TaskNotOwnedException,
    DatabaseException,
)
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

    def _check_for_duplicates(self, task_data: List[TaskRequest]) -> List[dict]:
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
        self, company_uuid: uuid.UUID, task_data: List[TaskRequest]
    ) -> Dict[str, Any]:
        try:
            # First check for duplicates within the provided data
            duplicates = self._check_for_duplicates(task_data)
            if duplicates:
                raise DuplicateTaskException(
                    "Duplicate tasks found in the request", duplicates
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
                raise TaskExistsException(
                    "Some tasks already exist in the database",
                    [
                        {"IDNO": t[0], "seria": t[1], "number": t[2]}
                        for t in existing_tasks
                    ],
                )

            # If no duplicates, proceed with creation
            self.task_repository.save_tasks(company_uuid, tasks)
            return {"message": "All tasks created successfully"}

        except DatabaseException as e:
            raise e
        except (DuplicateTaskException, TaskExistsException) as e:
            raise e
        except Exception as e:
            raise DatabaseException("Failed to create tasks", str(e))

    def get_tasks_status(
        self, company_uuid: uuid.UUID, task_data: List[TaskRequest]
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
            raise DatabaseException("Failed to get task status", str(e))

    def get_waiting_tasks_for_machine(
        self, company_uuid: uuid.UUID
    ) -> Dict[str, List[Dict[str, str]]]:
        """Get waiting tasks structured for machine processing"""
        try:
            # Get tasks from repository
            tasks = self.task_repository.get_waiting_tasks_by_company(company_uuid)

            # Structure the data
            result = {}
            for task in tasks:
                if task.IDNO not in result:
                    result[task.IDNO] = []
                result[task.IDNO].append(
                    {"seria": task.seria, "number": str(task.number)}
                )
            return result
        except Exception as e:
            raise DatabaseException("Failed to get waiting tasks", str(e))

    def update_tasks_status(
        self,
        company_uuid: uuid.UUID,
        task_data: List[TaskStatusUpdateRequest],
    ) -> Dict[str, Any]:
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

            # Verify tasks belong to the company
            for task in tasks:
                if not self.task_repository.task_belongs_to_company(
                    company_uuid, task.IDNO, task.seria, task.number
                ):
                    raise TaskNotOwnedException(
                        "One or more tasks do not belong to this company",
                        {
                            "IDNO": task.IDNO,
                            "seria": task.seria,
                            "number": task.number,
                        },
                    )

            # Update tasks in repository
            updated_count = self.task_repository.update_tasks_status(
                company_uuid, tasks, task_data
            )
            return {
                "message": f"Successfully updated {updated_count} tasks",
            }
        except TaskNotOwnedException as e:
            raise e
        except Exception as e:
            raise DatabaseException("Failed to update tasks status", str(e))
