import requests
import logging
from machine.config import Config
from machine.domain.schemas import MachineTasksResponse, TaskStatusUpdate
from typing import List


class APIClient:
    """Client for interacting with the server API"""

    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {Config.AUTH_TOKEN}",
            "Content-Type": "application/json",
        }
        self.logger = logging.getLogger(__name__)

    def get_tasks(self) -> MachineTasksResponse:
        """
        Fetch tasks from server.

        Returns:
            MachineTasksResponse: Object containing:
                - SingleInvoiceTask: Dict[str, List[SingleInvoiceTask]] - Tasks grouped by IDNO
                - MultipleInvoicesTask: List[MultipleInvoicesTask] - List of multiple invoice tasks

        Example Response:
        {
            "SingleInvoiceTask": {
                "200903003013": [
                    {
                        "seria": "AAEE13T",
                        "number": "312",
                        "task_uuid": "06a802aa-58de-4fd6-8cb6-f6fa2d11abca",
                        "action_type": "BuyerSignInvoice"
                    }
                ]
            },
            "MultipleInvoicesTask": [
                {
                    "my_company_idno": "2400903403013",
                    "task_uuid": "39ddb767-6d42-4f24-9a45-bf5f07ec1f7d",
                    "action_type": "SupplierSignAllDraftedInvoices"
                }
            ]
        }

        Raises:
            requests.exceptions.RequestException: If the API request fails
        """
        self.logger.info("Fetching tasks from server...")
        try:
            response = requests.get(
                Config.get_tasks_endpoint(), headers=self.headers, timeout=30
            )
            response.raise_for_status()

            tasks = response.json()
            self.logger.debug(f"Successfully fetched tasks: {tasks}")

            return MachineTasksResponse.model_validate(tasks)

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch tasks: {str(e)}")
            raise

    def update_task_status(self, task_updates: List[TaskStatusUpdate]) -> None:
        """
        Update status of tasks on the server.

        Args:
            task_updates: List of task status updates

        Example:
        ```python
        api_client.update_task_status([
            TaskStatusUpdate(
                task_uuid="3a040a48-33aa-4b1d-95cc-4882aa19bd0d",
                status=TaskStatus.COMPLETED
            )
        ])
        ```

        Raises:
            requests.exceptions.RequestException: If the API request fails
            HTTPError: If server returns 4XX or 5XX status code
        """
        self.logger.info("Updating task statuses...")
        try:
            # Convert task updates to list of dicts
            payload = [
                {"task_uuid": str(update.task_uuid), "status": update.status.value}
                for update in task_updates
            ]

            response = requests.put(
                Config.update_task_status_endpoint(),
                json=payload,
                headers=self.headers,
                timeout=30,
            )
            response.raise_for_status()

            self.logger.info("Successfully updated task statuses")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to update task statuses: {str(e)}")
            raise
