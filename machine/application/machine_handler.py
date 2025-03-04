import time
import logging
from machine.config import Config, USB_PIN
from machine.domain.models.dataclass.dataclass import Worker
from machine.domain.schemas import TaskStatusUpdate, TaskStatus
from machine.infrastructure.api_client import APIClient
from machine.infrastructure.selenium.web_driver_manager import WebDriverManager
from machine.infrastructure.selenium.login_handler import SeleniumLoginHandler
from machine.infrastructure.desktop.msign_handler import MSignDesktopHandler
from machine.domain.task_executor import TaskExecutor
from machine.application.login_service import LoginService
from typing import List


class MachineHandler:
    def __init__(self, environment="TEST"):
        self.environment = environment
        self.api_client = APIClient()
        self.driver_manager = WebDriverManager()
        self.logger = logging.getLogger(__name__)

    def process_single_invoice_tasks(self, tasks_by_company) -> list[TaskStatusUpdate]:
        """Process single invoice tasks for each company"""
        all_results = []

        for certificate_name, company_tasks in tasks_by_company.items():
            for my_company_idno, invoice_tasks in company_tasks.items():
                try:
                    # Initialize new driver and handlers for each company
                    driver = self.driver_manager.get_driver()
                    web_handler = SeleniumLoginHandler(driver, self.environment)
                    desktop_handler = MSignDesktopHandler()

                    # Initialize services
                    login_service = LoginService(web_handler, desktop_handler)
                    task_executor = TaskExecutor(web_handler, desktop_handler)

                    try:
                        # Get PIN and create worker
                        pin = USB_PIN.get_pin(certificate_name)
                        worker = Worker(
                            my_company_idno=my_company_idno,
                            pin=pin,
                            person_name_certificate=certificate_name,
                        )

                        # Login worker
                        login_service.login_worker(worker)

                        # Execute tasks with worker instance
                        results = task_executor.execute_single_invoice_tasks(
                            worker, invoice_tasks
                        )
                        all_results.extend(results)

                    finally:
                        # Always close the driver
                        self.driver_manager.close_driver(driver)

                except Exception:
                    self.logger.error(
                        f"Failed to process tasks for company {my_company_idno}",
                        exc_info=True,
                    )
                    # Add failed status for all tasks of this company
                    for task in invoice_tasks:
                        all_results.append(
                            TaskStatusUpdate(
                                task_uuid=task["task_uuid"], status=TaskStatus.FAILED
                            )
                        )

        return all_results

    def process_multiple_invoice_tasks(
        self, tasks_by_company: List[dict]
    ) -> List[TaskStatusUpdate]:
        """Process multiple invoice tasks"""
        all_results = []

        try:
            for certificate_name, company_tasks in tasks_by_company.items():
                for my_company_idno, invoice_tasks in company_tasks.items():

                    # Initialize new driver and handlers for each company
                    driver = self.driver_manager.get_driver()
                    web_handler = SeleniumLoginHandler(driver, self.environment)
                    desktop_handler = MSignDesktopHandler()

                    # Initialize services
                    login_service = LoginService(web_handler, desktop_handler)
                    task_executor = TaskExecutor(web_handler, desktop_handler)

                    # Get PIN and create worker
                    pin = USB_PIN.get_pin(certificate_name)
                    worker = Worker(
                        my_company_idno=my_company_idno,
                        pin=pin,
                        person_name_certificate=certificate_name,
                    )

                    # Login worker
                    login_service.login_worker(worker)

                    # Execute task with worker instance

                    result = task_executor.execute_multiple_invoice_tasks(
                        worker, invoice_tasks
                    )
                    all_results.append(result)

        except Exception as e:
            self.logger.error(
                f"Failed to process task for company {invoice_tasks.get('my_company_idno')}: {str(e)}",
                exc_info=True,
            )
            all_results.append(
                TaskStatusUpdate(
                    task_uuid=invoice_tasks.get("task_uuid"), status=TaskStatus.FAILED
                )
            )

        finally:
            # Always close the driver
            self.driver_manager.close_driver(driver)

        return all_results

    def run(self):
        """Main loop to check and process tasks"""
        while True:
            try:
                self.logger.info("Checking for new tasks...")
                tasks_response = self.api_client.get_tasks()

                if tasks_response.SingleInvoiceTask:
                    results = self.process_single_invoice_tasks(
                        tasks_response.SingleInvoiceTask
                    )
                    self.api_client.update_task_status(results)

                if tasks_response.MultipleInvoicesTask:
                    results = self.process_multiple_invoice_tasks(
                        tasks_response.MultipleInvoicesTask
                    )
                    self.api_client.update_task_status(results)

            except Exception as e:
                self.logger.error(f"Error in main loop: {str(e)}", exc_info=True)

            self.logger.info(
                f"Waiting {Config.POLL_INTERVAL} seconds before next check"
            )
            time.sleep(Config.POLL_INTERVAL)
