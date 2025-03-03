import os
from dotenv import load_dotenv
from machine.domain.exceptions import IDNONotFoundException, NoPinFoundException

load_dotenv()


class Config:
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    API_BASE_URL = os.getenv("SERVER_URL", "http://localhost:7989")
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))  # in seconds
    TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", 300))  # in seconds

    # API Endpoints
    @staticmethod
    def get_tasks_endpoint():
        return f"{Config.API_BASE_URL}/machine/tasks"

    @staticmethod
    def update_task_status_endpoint():
        return f"{Config.API_BASE_URL}/tasks/status"


class USB_PIN:
    """Configuration for USB PINs mapped to company IDNOs"""

    # Map IDNO to environment variable names
    IDNO_MAP = {
        "1024600012882": "CONFIRM_SOLUTIONS_PIN",
    }

    @classmethod
    def get_pin(cls, my_company_idno: str) -> str:
        """Get USB PIN for a company IDNO."""
        if my_company_idno not in cls.IDNO_MAP:
            raise IDNONotFoundException(my_company_idno)

        env_var = cls.IDNO_MAP[my_company_idno]
        pin = os.getenv(env_var)

        if not pin:
            raise NoPinFoundException(env_var)

        return pin
