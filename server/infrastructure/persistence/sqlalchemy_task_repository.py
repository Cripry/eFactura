from domain.task.repository import TaskRepository
from domain.task.models import (
    MultipleInvoicesTaskDataModel,
    SingleInvoiceTaskDataModel,
    CompanyTaskModel,
)
from sqlalchemy import exc
from domain.exceptions import DatabaseException, TaskNotFoundException
import uuid
from typing import List
from uuid import UUID
from domain.task.schemas import (
    SingleInvoiceStatusRequest,
    TaskStatus,
    MultipleInvoicesAction,
    MultipleInvoicesIdentifier,
    MultipleInvoicesResponse,
    SingleInvoiceIdentifier,
    SingleInvoiceAction,
    SingleInvoiceResponse,
    TaskStatusResponse,
    TaskStatusUpdateByUUIDRequest,
    TaskType,
    TaskStatusItem,
)


class SQLAlchemyTaskRepository(TaskRepository):
    """Repository implementation for task-related database operations using SQLAlchemy."""

    def __init__(self, session):
        self.session = session

    def verify_company_task_ownership(
        self, company_uuid: UUID, tasks_uuid: List[UUID]
    ) -> bool:
        """
        Verify that all specified tasks belong to the company.

        Args:
            company_uuid: UUID of the company
            tasks_uuid: List of task UUIDs to verify

        Returns:
            bool: True if all tasks belong to the company

        Raises:
            TaskNotFoundException: If a task doesn't exist
            DatabaseException: If there's a database error
        """
        try:
            # Check if all tasks exist
            for task_uuid in tasks_uuid:
                if not self.verify_company_task_exists(task_uuid):
                    raise TaskNotFoundException("Task not found", task_uuid)

            # Count how many of the provided tasks belong to the company
            matching_tasks_count = (
                self.session.query(CompanyTaskModel)
                .filter(
                    CompanyTaskModel.company_uuid == company_uuid,
                    CompanyTaskModel.task_uuid.in_(tasks_uuid),
                )
                .count()
            )

            # If the count matches the number of tasks provided, all tasks belong to the company
            return matching_tasks_count == len(tasks_uuid)

        except TaskNotFoundException as e:
            raise TaskNotFoundException(str(e), e.task_uuid)
        except DatabaseException as e:
            raise DatabaseException("Failed to verify tasks ownership", str(e))

    def verify_company_task_exists(self, task_uuid: UUID) -> bool:
        """
        Check if a task exists in the database.

        Args:
            task_uuid: UUID of the task to check

        Returns:
            bool: True if the task exists

        Raises:
            DatabaseException: If there's a database error
        """
        try:
            task = (
                self.session.query(CompanyTaskModel)
                .filter(CompanyTaskModel.task_uuid == task_uuid)
                .first()
            )
            return task is not None
        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to verify task exists", str(e))

    def create_single_invoice_entry(
        self,
        action_type: SingleInvoiceAction,
        invoice: SingleInvoiceIdentifier,
    ) -> SingleInvoiceTaskDataModel:
        """
        Create a new single invoice task entry.

        Args:
            action_type: Type of action to perform
            invoice: Invoice details

        Returns:
            SingleInvoiceTaskDataModel: Created task entry

        Raises:
            DatabaseException: If there's an error saving to the database
        """
        try:
            task = SingleInvoiceTaskDataModel(
                task_uuid=uuid.uuid4(),
                my_company_idno=invoice.my_company_idno,
                person_name_certificate=invoice.person_name_certificate,
                seria=invoice.seria,
                number=invoice.number,
                action_type=action_type,
            )
            self.session.add(task)
            self.session.commit()

            return task

        except exc.IntegrityError as e:
            self.session.rollback()
            raise DatabaseException("Database integrity error", str(e.orig))
        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to save tasks", str(e))

    def create_multiple_invoice_entry(
        self,
        action_type: MultipleInvoicesAction,
        invoice: MultipleInvoicesIdentifier,
    ) -> MultipleInvoicesTaskDataModel:
        try:
            task = MultipleInvoicesTaskDataModel(
                task_uuid=uuid.uuid4(),
                my_company_idno=invoice.my_company_idno,
                person_name_certificate=invoice.person_name_certificate,
                buyer_idno=invoice.buyer_idno,
                signature_type=invoice.signature_type,
                action_type=action_type,
            )
            self.session.add(task)
            self.session.commit()

            return task

        except exc.IntegrityError as e:
            self.session.rollback()
            raise DatabaseException("Database integrity error", str(e.orig))
        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to save tasks", str(e))

    def get_single_invoice_tasks_status(
        self, tasks: List[SingleInvoiceStatusRequest]
    ) -> TaskStatusResponse:
        try:
            # Get task statuses by joining tables and filtering
            task_statuses = (
                self.session.query(
                    SingleInvoiceTaskDataModel.my_company_idno,
                    SingleInvoiceTaskDataModel.seria,
                    SingleInvoiceTaskDataModel.number,
                    CompanyTaskModel.status,
                )
                .join(
                    CompanyTaskModel,
                    CompanyTaskModel.task_uuid == SingleInvoiceTaskDataModel.task_uuid,
                )
                .filter(
                    SingleInvoiceTaskDataModel.my_company_idno.in_(
                        [task.my_company_idno for task in tasks]
                    ),
                    SingleInvoiceTaskDataModel.seria.in_(
                        [task.seria for task in tasks]
                    ),
                    SingleInvoiceTaskDataModel.number.in_(
                        [task.number for task in tasks]
                    ),
                )
                .all()
            )

            # Convert to response format
            return TaskStatusResponse(
                tasks=[
                    TaskStatusItem(
                        my_company_idno=status.my_company_idno,
                        seria=status.seria,
                        number=str(
                            status.number
                        ),  # Convert to string since schema expects string
                        status=status.status,
                    )
                    for status in task_statuses
                ]
            )

        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to get tasks status", str(e))

    def update_tasks_status(
        self,
        updated_tasks_data: List[TaskStatusUpdateByUUIDRequest],
    ) -> None:
        """
        Update status of multiple tasks.

        Args:
            updated_tasks_data: List of tasks with their new statuses

        Raises:
            DatabaseException: If there's an error updating the database
        """
        try:
            for updated_task_data in updated_tasks_data:
                # task_uuid is already UUID type from the schema
                self.session.query(CompanyTaskModel).filter(
                    CompanyTaskModel.task_uuid == updated_task_data.task_uuid
                ).update({CompanyTaskModel.status: updated_task_data.status})

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to update tasks status", str(e))

    def get_waiting_tasks_for_machine_single_invoice(self, company_uuid: uuid.UUID):
        try:
            # Single query joining CompanyTaskModel with SingleInvoiceTaskDataModel
            waiting_tasks = (
                self.session.query(
                    SingleInvoiceTaskDataModel.my_company_idno,
                    SingleInvoiceTaskDataModel.seria,
                    SingleInvoiceTaskDataModel.number,
                    SingleInvoiceTaskDataModel.person_name_certificate,
                    CompanyTaskModel.task_uuid,
                    SingleInvoiceTaskDataModel.action_type,
                )
                .join(
                    CompanyTaskModel,
                    CompanyTaskModel.task_uuid == SingleInvoiceTaskDataModel.task_uuid,
                )
                .filter(
                    CompanyTaskModel.company_uuid == company_uuid,
                    CompanyTaskModel.status == TaskStatus.WAITING.value,
                    CompanyTaskModel.task_type == TaskType.SINGLE_INVOICE_TASK.value,
                )
                .all()
            )

            return [
                SingleInvoiceResponse(
                    my_company_idno=task.my_company_idno,
                    seria=task.seria,
                    person_name_certificate=task.person_name_certificate,
                    number=task.number,
                    task_uuid=str(task.task_uuid),
                    action_type=task.action_type,
                )
                for task in waiting_tasks
            ]

        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to get waiting tasks", str(e))

    def get_waiting_tasks_for_machine_multiple_invoices(
        self, company_uuid: uuid.UUID
    ) -> List[MultipleInvoicesResponse]:
        try:
            # Single query joining CompanyTaskModel with MultipleInvoicesTaskDataModel
            waiting_tasks = (
                self.session.query(
                    MultipleInvoicesTaskDataModel.my_company_idno,
                    MultipleInvoicesTaskDataModel.person_name_certificate,
                    MultipleInvoicesTaskDataModel.buyer_idno,
                    MultipleInvoicesTaskDataModel.signature_type,
                    CompanyTaskModel.task_uuid,
                    MultipleInvoicesTaskDataModel.action_type,
                )
                .join(
                    CompanyTaskModel,
                    CompanyTaskModel.task_uuid
                    == MultipleInvoicesTaskDataModel.task_uuid,
                )
                .filter(
                    CompanyTaskModel.company_uuid == company_uuid,
                    CompanyTaskModel.status == TaskStatus.WAITING.value,
                    CompanyTaskModel.task_type == TaskType.MULTIPLE_INVOICES_TASK.value,
                )
                .all()
            )

            return [
                MultipleInvoicesResponse(
                    my_company_idno=task.my_company_idno,
                    task_uuid=str(task.task_uuid),
                    person_name_certificate=task.person_name_certificate,
                    buyer_idno=task.buyer_idno,
                    signature_type=task.signature_type,
                    action_type=task.action_type,
                )
                for task in waiting_tasks
            ]

        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to get waiting tasks", str(e))

    def single_invoice_entry_exists(
        self,
        my_company_idno: str,
        seria: str,
        number: int,
        person_name_certificate: str,
    ) -> bool:
        try:
            task = (
                self.session.query(SingleInvoiceTaskDataModel)
                .filter(
                    SingleInvoiceTaskDataModel.my_company_idno == my_company_idno,
                    SingleInvoiceTaskDataModel.seria == seria,
                    SingleInvoiceTaskDataModel.number == number,
                    SingleInvoiceTaskDataModel.person_name_certificate
                    == person_name_certificate,
                )
                .first()
            )

            return task is not None

        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to check if task exists", str(e))

    def create_company_task(
        self,
        task_uuid: UUID,
        company_uuid: UUID,
        status: TaskStatus,
        task_type: TaskType,
    ):
        """
        Create a company task association.

        Args:
            task_uuid: UUID of the task
            company_uuid: UUID of the company
            status: Initial status of the task
            task_type: Type of the task (Single/Multiple)

        Raises:
            DatabaseException: If there's an error saving to the database
        """
        try:
            task = CompanyTaskModel(
                task_uuid=task_uuid,
                company_uuid=company_uuid,
                status=status,
                task_type=task_type,
            )
            self.session.add(task)
            self.session.commit()

        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to create company task", str(e))

    def get_single_invoice_tasks_uuid(
        self, tasks: List[SingleInvoiceStatusRequest]
    ) -> List[uuid.UUID]:
        try:
            tasks_my_company_idno = [task.my_company_idno for task in tasks]
            tasks_seria = [task.seria for task in tasks]
            tasks_number = [task.number for task in tasks]

            tasks_uuid = (
                self.session.query(SingleInvoiceTaskDataModel)
                .filter(
                    SingleInvoiceTaskDataModel.my_company_idno.in_(
                        tasks_my_company_idno
                    ),
                    SingleInvoiceTaskDataModel.seria.in_(tasks_seria),
                    SingleInvoiceTaskDataModel.number.in_(tasks_number),
                )
                .all()
            )

            return [task.task_uuid for task in tasks_uuid]

        except Exception as e:
            self.session.rollback()
            raise DatabaseException("Failed to get tasks uuid", str(e))

    def create_single_invoice_task(self, company_uuid: UUID, task_data: dict) -> None:
        try:
            task = SingleInvoiceTaskDataModel(
                task_uuid=uuid.uuid4(),
                company_uuid=company_uuid,
                my_company_idno=task_data["my_company_idno"],
                person_name_certificate=task_data["person_name_certificate"],
                seria=task_data["seria"],
                number=task_data["number"],
                action_type=task_data["action_type"],
                status="WAITING",
            )
            self.session.add(task)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise DatabaseException(f"Error creating task: {str(e)}", str(e))

    def create_multiple_invoices_task(
        self, company_uuid: UUID, task_data: dict
    ) -> None:
        try:
            task = MultipleInvoicesTaskDataModel(
                task_uuid=uuid.uuid4(),
                company_uuid=company_uuid,
                my_company_idno=task_data["my_company_idno"],
                person_name_certificate=task_data["person_name_certificate"],
                action_type=task_data["action_type"],
                status="WAITING",
            )
            self.session.add(task)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise DatabaseException(f"Error creating task: {str(e)}", str(e))
