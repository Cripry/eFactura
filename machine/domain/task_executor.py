from typing import List
from domain.models import CompanyTasks, Task, TaskResult, TaskStatus
from domain.exceptions import USBNotFoundException
import logging


class TaskExecutor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def execute_tasks(self, company_tasks: List[CompanyTasks]) -> List[TaskResult]:
        self.logger.info(f"Executing {len(company_tasks)} company tasks")
        results = []
        for ct in company_tasks:
            self.logger.debug(f"Processing tasks for company {ct.idno}")
            for task in ct.tasks:
                try:
                    self.logger.debug(f"Executing task: {task}")
                    self._execute_single_task(ct.idno, task)
                    results.append(
                        TaskResult(
                            idno=ct.idno,
                            seria=task.seria,
                            number=task.number,
                            status=TaskStatus.COMPLETED,
                        )
                    )
                    self.logger.debug("Task completed successfully")
                except USBNotFoundException as e:
                    self.logger.warning(f"USB not found for task: {task}")
                    results.append(
                        TaskResult(
                            idno=ct.idno,
                            seria=task.seria,
                            number=task.number,
                            status=TaskStatus.USB_NOT_FOUND,
                            error=str(e),
                        )
                    )
                except Exception as e:
                    self.logger.error(f"Error executing task: {task}", exc_info=True)
                    results.append(
                        TaskResult(
                            idno=ct.idno,
                            seria=task.seria,
                            number=task.number,
                            status=TaskStatus.FAILED,
                            error=str(e),
                        )
                    )
        self.logger.info(f"Completed execution of {len(results)} tasks")
        return results

    def _execute_single_task(self, idno: str, task: Task):
        self.logger.debug(f"Executing single task for company {idno}: {task}")
        # Placeholder for actual task execution
        return True
