from domain.company.company import Company
from domain.task.repository import TaskRepository
from domain.task.schemas import (
    SingleInvoiceStatusRequest,
    TaskStatus,
    MultipleInvoicesResponse,
    SingleInvoiceIdentifier,
    MultipleInvoicesAction,
    MultipleInvoicesIdentifier,
    SingleInvoiceAction,
    SingleInvoiceResponse,
    TaskStatusUpdateByUUIDRequest,
    TaskType,
)
from typing import List, Union
from domain.exceptions import (
    DatabaseException,
    DuplicateTaskException,
    TaskExistsException,
    TaskNotOwnedException,
    TaskNotFoundException,
)


class TaskService:
    """Service layer for handling task-related business logic."""

    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def _get_existing_single_invoice_tasks(
        self, single_invoice_tasks: List[SingleInvoiceIdentifier]
    ) -> List[dict]:
        """Check if any of the tasks already exist in the database"""
        existing_tasks = []
        for single_invoice_task in single_invoice_tasks:
            if self.task_repository.single_invoice_entry_exists(
                single_invoice_task.idno,
                single_invoice_task.seria,
                single_invoice_task.number,
            ):
                existing_tasks.append(
                    {
                        "idno": single_invoice_task.idno,
                        "seria": single_invoice_task.seria,
                        "number": single_invoice_task.number,
                    }
                )
        return existing_tasks

    def _check_for_duplicates(
        self, tasks: List[Union[SingleInvoiceIdentifier, MultipleInvoicesIdentifier]]
    ) -> List[dict]:
        """Check for duplicates within the provided task data"""
        seen = set()
        duplicates = []
        for task in tasks:

            if isinstance(task, SingleInvoiceIdentifier):
                task_key = (
                    task.idno,
                    task.seria,
                    task.number,
                )
            else:
                task_key = task.idno

            if task_key in seen:
                duplicates.append(task_key)
            else:
                seen.add(task_key)
        return duplicates

    def create_single_invoice_task(
        self,
        current_company: Company,
        action_type: SingleInvoiceAction,
        invoices: List[SingleInvoiceIdentifier],
    ):
        """
        Create tasks for signing individual invoices as a buyer.

        Args:
            current_company: Company entity making the request
            action_type: Type of action to perform (e.g., BuyerSignInvoice)
            invoices: List of invoices to be signed

        Raises:
            TaskExistsException: If any of the tasks already exist
            DuplicateTaskException: If there are duplicate invoices in the request
            DatabaseException: If there's an error saving to the database
        """
        # 1. Check if the task already exists
        existing_tasks = self._get_existing_single_invoice_tasks(invoices)
        if existing_tasks:
            raise TaskExistsException(
                "Tasks already exist in database", existing_tasks=existing_tasks
            )

        # 2. Check for duplicates
        duplicates = self._check_for_duplicates(invoices)
        if duplicates:
            raise DuplicateTaskException("Duplicates found", duplicates=duplicates)

        for invoice in invoices:
            # 3. Create the single invoice entry
            single_invoice_entry = self.task_repository.create_single_invoice_entry(
                action_type=action_type, invoice=invoice
            )

            # 4. Create the company task
            self.task_repository.create_company_task(
                task_uuid=single_invoice_entry.task_uuid,
                company_uuid=current_company.company_uuid,
                status=TaskStatus.WAITING.value,
                task_type=TaskType.SINGLE_INVOICE_TASK.value,
            )

    def create_multiple_invoices_task(
        self,
        current_company: Company,
        action_type: MultipleInvoicesAction,
        invoices: List[MultipleInvoicesIdentifier],
    ):
        """
        Create tasks for signing all invoices from a specific page.

        Args:
            current_company: Company entity making the request
            action_type: Type of action and page to process (e.g., SupplierSignAllDraftedInvoices)
            invoices: List of company IDNOs to process

        Raises:
            DuplicateTaskException: If there are duplicate IDNOs in the request
            DatabaseException: If there's an error saving to the database
        """
        # 1. Check if the task already exists
        duplicates = self._check_for_duplicates(invoices)
        if duplicates:
            raise DuplicateTaskException(f"Duplicates found: {duplicates}")

        for invoice in invoices:
            # 3. Create the multiple invoices entry
            multuple_invoice_entry = self.task_repository.create_multiple_invoice_entry(
                action_type=action_type, invoice=invoice
            )

            # 4. Create the company tasks
            self.task_repository.create_company_task(
                task_uuid=multuple_invoice_entry.task_uuid,
                company_uuid=current_company.company_uuid,
                status=TaskStatus.WAITING.value,
                task_type=TaskType.MULTIPLE_INVOICES_TASK.value,
            )

    def get_single_invoice_tasks_status(
        self, current_company: Company, tasks: List[SingleInvoiceStatusRequest]
    ):
        """
        Get status of specified single invoice tasks.

        Args:
            current_company: Company entity making the request
            tasks: List of invoice identifiers to check status for

        Returns:
            TaskStatusResponse: List of tasks with their current status

        Raises:
            TaskNotOwnedException: If tasks don't belong to the company
            DatabaseException: If there's an error retrieving from the database
        """
        # 1. Check if the tasks belongs to the company
        tasks_uuid = self.task_repository.get_single_invoice_tasks_uuid(tasks)

        tasks_belongs_to_company = self.task_repository.verify_company_task_ownership(
            current_company.company_uuid, tasks_uuid
        )
        if not tasks_belongs_to_company:
            raise TaskNotOwnedException("Tasks do not belong to the company")

        # 2. Get the tasks status
        tasks_status = self.task_repository.get_single_invoice_tasks_status(tasks)

        return tasks_status

    def update_tasks_status_by_uuid(
        self, current_company: Company, request: List[TaskStatusUpdateByUUIDRequest]
    ):
        """
        Update status of multiple tasks by their UUIDs.

        Args:
            current_company: Company entity making the request
            request: List of task UUIDs and their new statuses

        Raises:
            TaskNotFoundException: If a task UUID doesn't exist
            TaskNotOwnedException: If tasks don't belong to the company
            DatabaseException: If there's an error updating the database
        """
        try:
            # 1. Check if the tasks belongs to the company
            tasks_uuid = [task.task_uuid for task in request]  # Already UUID objects
            tasks_belongs_to_company = (
                self.task_repository.verify_company_task_ownership(
                    current_company.company_uuid, tasks_uuid
                )
            )
            if not tasks_belongs_to_company:
                raise TaskNotOwnedException("Tasks do not belong to the company")

            # 2. Update the tasks status
            self.task_repository.update_tasks_status(request)

        except TaskNotFoundException as e:
            raise TaskNotFoundException(e.message, e.task_uuid)
        except TaskNotOwnedException as e:
            raise TaskNotOwnedException(str(e))
        except DatabaseException as e:
            raise DatabaseException("Failed to update tasks status", str(e))

    def get_waiting_tasks_for_machine_single_invoice(
        self, current_company: Company
    ) -> List[SingleInvoiceResponse]:
        """
        Returns a list with SingleInvoiceResponse for each task that is waiting for the machine
        """
        try:
            # 1. Get the waiting tasks
            waiting_tasks = (
                self.task_repository.get_waiting_tasks_for_machine_single_invoice(
                    current_company.company_uuid
                )
            )

            return waiting_tasks

        except DatabaseException as e:
            raise DatabaseException("Failed to get waiting tasks", str(e))

    def get_waiting_tasks_for_machine_multiple_invoices(
        self, current_company: Company
    ) -> List[MultipleInvoicesResponse]:
        """
        Returns a list with MultipleInvoicesResponse for each task that is waiting for the machine
        """
        try:
            # 1. Get the waiting tasks
            waiting_tasks = (
                self.task_repository.get_waiting_tasks_for_machine_multiple_invoices(
                    current_company.company_uuid
                )
            )

            return waiting_tasks

        except DatabaseException as e:
            raise DatabaseException("Failed to get waiting tasks", str(e))

    def get_structured_waiting_tasks_for_machine(
        self, current_company: Company
    ) -> dict:
        """
        Get all waiting tasks organized by type for the machine.

        Args:
            current_company: Company entity making the request

        Returns:
            dict: Tasks structured by type:
                - SingleInvoiceTask: Grouped by IDNO
                - MultipleInvoicesTask: List of tasks

        Raises:
            DatabaseException: If there's an error retrieving from the database
        """
        try:
            # Get tasks from both sources
            single_invoice_tasks = self.get_waiting_tasks_for_machine_single_invoice(
                current_company
            )
            multiple_invoices_tasks = (
                self.get_waiting_tasks_for_machine_multiple_invoices(current_company)
            )

            # Group single invoice tasks by IDNO
            single_invoice_grouped = {}
            for task in single_invoice_tasks:
                if task.idno not in single_invoice_grouped:
                    single_invoice_grouped[task.idno] = []
                single_invoice_grouped[task.idno].append(
                    {
                        "seria": task.seria,
                        "number": task.number,
                        "task_uuid": task.task_uuid,
                        "action_type": task.action_type,
                    }
                )

            # Structure the final response
            result = {
                TaskType.SINGLE_INVOICE_TASK.value: single_invoice_grouped,
                TaskType.MULTIPLE_INVOICES_TASK.value: [
                    {
                        "idno": task.idno,
                        "task_uuid": task.task_uuid,
                        "action_type": task.action_type,
                    }
                    for task in multiple_invoices_tasks
                ],
            }

            return result

        except DatabaseException as e:
            raise DatabaseException("Failed to get structured waiting tasks", str(e))
