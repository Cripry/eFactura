import logging
from typing import List
from machine.domain.models import TaskStatus
from machine.domain.exceptions import USBNotFoundException
from machine.domain.schemas import TaskStatusUpdate
from machine.domain.models.dataclass.dataclass import Worker
from machine.domain.services.buyer_role_efactura import BuyerRoleEfactura
from machine.domain.services.supplier_role_efactura import SupplierRoleEfactura


class TaskExecutor:
    def __init__(self, web_handler, desktop_handler):
        self.web_handler = web_handler
        self.desktop_handler = desktop_handler
        self.logger = logging.getLogger(__name__)

    def execute_single_invoice_tasks(
        self, worker: Worker, tasks: List[dict]
    ) -> List[TaskStatusUpdate]:
        """Execute single invoice tasks for a specific company"""
        self.logger.info(
            f"Processing {len(tasks)} tasks for company {worker.my_company_idno}"
        )
        results = []

        try:
            # Create service with provided worker
            buyer_service = BuyerRoleEfactura(
                worker, self.web_handler, self.desktop_handler
            )

            # Process each task
            for task in tasks:
                try:
                    self.logger.info(f"Processing task: {task}")
                    buyer_service.sign_invoice(task["seria"], task["number"])

                    results.append(
                        TaskStatusUpdate(
                            task_uuid=task["task_uuid"], status=TaskStatus.COMPLETED
                        )
                    )

                except USBNotFoundException:
                    self.logger.warning(f"USB not found for task: {task}")
                    results.append(
                        TaskStatusUpdate(
                            task_uuid=task["task_uuid"], status=TaskStatus.USB_NOT_FOUND
                        )
                    )
                except Exception:
                    self.logger.error(f"Failed to process task: {task}", exc_info=True)
                    results.append(
                        TaskStatusUpdate(
                            task_uuid=task["task_uuid"], status=TaskStatus.FAILED
                        )
                    )

        except Exception:
            self.logger.error(
                f"Failed to process tasks for company {worker.my_company_idno}",
                exc_info=True,
            )
            # Add FAILED status for all remaining tasks
            for task in tasks:
                if not any(r.task_uuid == task["task_uuid"] for r in results):
                    results.append(
                        TaskStatusUpdate(
                            task_uuid=task["task_uuid"], status=TaskStatus.FAILED
                        )
                    )

        return results

    def execute_multiple_invoice_tasks(
        self, worker: Worker, task: dict
    ) -> TaskStatusUpdate:
        """Execute multiple invoice task for a specific company"""
        self.logger.info(
            f"Processing multiple invoice task for company {worker.my_company_idno}"
        )

        try:
            action_type = task["action_type"]
            task_uuid = task["task_uuid"]

            if action_type == "SupplierSignAllDraftedInvoices":
                # Create supplier service
                supplier_service = SupplierRoleEfactura(
                    worker, self.web_handler, self.desktop_handler
                )

                try:
                    # Execute signing
                    supplier_service.sign_all_invoices()
                    return TaskStatusUpdate(
                        task_uuid=task_uuid, status=TaskStatus.COMPLETED
                    )
                except Exception as e:
                    self.logger.error(
                        f"Failed to sign all invoices for company {worker.my_company_idno}: {str(e)}",
                        exc_info=True,
                    )
                    return TaskStatusUpdate(
                        task_uuid=task_uuid, status=TaskStatus.FAILED
                    )
            else:
                self.logger.warning(f"Unknown action type: {action_type}")
                return TaskStatusUpdate(task_uuid=task_uuid, status=TaskStatus.FAILED)

        except Exception as e:
            self.logger.error(
                f"Failed to process task for company {worker.my_company_idno}: {str(e)}",
                exc_info=True,
            )
            return TaskStatusUpdate(
                task_uuid=task["task_uuid"], status=TaskStatus.FAILED
            )
