import requests
from typing import List
from config import Config
from domain.models import TaskResult, MachineTasksResponse
import logging


class APIClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {Config.AUTH_TOKEN}",
            "Content-Type": "application/json",
        }
        self.logger = logging.getLogger(__name__)

    def get_tasks(self) -> MachineTasksResponse:
        self.logger.info("Fetching tasks from server...")
        response = requests.get(Config.get_tasks_endpoint(), headers=self.headers)
        response.raise_for_status()
        self.logger.debug("Successfully fetched tasks from server")
        return MachineTasksResponse.model_validate(response.json())

    def update_task_status(self, task_results: List[TaskResult]):
        self.logger.info("Updating task statuses on server...")
        payload = [
            {
                "IDNO": result.idno,
                "seria": result.seria,
                "number": result.number,
                "status_update": result.status.value,
            }
            for result in task_results
        ]
        self.logger.debug(f"Sending status update payload: {payload}")
        response = requests.put(
            Config.update_task_status_endpoint(), json=payload, headers=self.headers
        )
        response.raise_for_status()
        self.logger.info("Successfully updated task statuses")
