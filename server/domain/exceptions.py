class BusinessException(Exception):
    """Base class for all business exceptions"""

    def __init__(self, message: str, code: str):
        super().__init__(message)
        self.message = message
        self.code = code


class DuplicateTaskException(BusinessException):
    """Raised when duplicate tasks are found"""

    def __init__(self, message: str, duplicates: list):
        super().__init__(message, "DUPLICATE_TASKS")
        self.duplicates = duplicates


class TaskExistsException(BusinessException):
    """Raised when tasks already exist in database"""

    def __init__(self, message: str, existing_tasks: list):
        super().__init__(message, "TASKS_EXIST")
        self.existing_tasks = existing_tasks


class InvalidStatusException(BusinessException):
    """Raised when invalid task status is provided"""

    def __init__(self, message: str):
        super().__init__(message, "INVALID_STATUS")


class TaskNotOwnedException(BusinessException):
    """Raised when tasks don't belong to company"""

    def __init__(self, message: str, task_details: dict):
        super().__init__(message, "TASK_NOT_OWNED")
        self.task_details = task_details


class DatabaseException(BusinessException):
    """Raised for database related errors"""

    def __init__(self, message: str, details: str):
        super().__init__(message, "DATABASE_ERROR")
        self.details = details


class CompanyNotFoundException(Exception):
    """Exception raised when a company is not found"""

    def __init__(self, message: str):
        super().__init__(message)
