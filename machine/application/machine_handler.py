import time
import logging
from typing import Dict, List
from config import Config
from domain.models import CompanyTasks, Task
from infrastructure.api_client import APIClient
from domain.task_executor import TaskExecutor


class MachineHandler:
    def __init__(self):
        self.api_client = APIClient()
        self.task_executor = TaskExecutor()
        self.logger = logging.getLogger(__name__)

    def run(self):
        while True:
            try:
                self.logger.info("Checking for new tasks...")
                tasks_response = self.api_client.get_tasks()

                if tasks_response.root:
                    self.logger.info(f"Received {len(tasks_response.root)} tasks")
                    self.logger.debug(f"Tasks received: {tasks_response.root}")

                    company_tasks = self._parse_tasks(tasks_response.root)
                    self.logger.info(f"Parsed {len(company_tasks)} company tasks")

                    results = self.task_executor.execute_tasks(company_tasks)
                    self.logger.info(f"Executed {len(results)} tasks")
                    self.logger.debug(f"Execution results: {results}")

                    self.logger.info("Sending status updates to server...")
                    self.api_client.update_task_status(results)
                    self.logger.info("Status updates sent successfully")
                else:
                    self.logger.info("No tasks available")

            except Exception as e:
                self.logger.error(f"Error processing tasks: {str(e)}", exc_info=True)
                self.logger.info("Retrying after error...")

            self.logger.info(
                f"Waiting {Config.POLL_INTERVAL} seconds before next check"
            )
            time.sleep(Config.POLL_INTERVAL)

    def _parse_tasks(
        self, tasks: Dict[str, List[Dict[str, str]]]
    ) -> List[CompanyTasks]:
        self.logger.debug("Parsing tasks from server response")
        parsed_tasks = [
            CompanyTasks(
                idno=idno,
                tasks=[
                    Task(seria=t["seria"], number=int(t["number"])) for t in task_list
                ],
            )
            for idno, task_list in tasks.items()
        ]
        self.logger.debug(f"Parsed tasks: {parsed_tasks}")
        return parsed_tasks
