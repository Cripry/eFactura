import json
from pathlib import Path
from dotenv import load_dotenv
from machine.domain.exceptions import IDNONotFoundException, NoPinFoundException

load_dotenv()

CONFIG_PATH = Path(__file__).parent / "config.json"


class Config:
    _CONFIG_DATA = None

    @classmethod
    def _load_config(cls):
        if cls._CONFIG_DATA is None:
            try:
                with open(CONFIG_PATH, "r") as f:
                    cls._CONFIG_DATA = json.load(f)
            except FileNotFoundError:
                raise NoPinFoundException("config.json file not found")
            except json.JSONDecodeError:
                raise NoPinFoundException("Invalid JSON format in config.json")

    @classmethod
    @property
    def AUTH_TOKEN(cls):
        cls._load_config()
        return cls._CONFIG_DATA["api"].get("AUTH_TOKEN")

    @classmethod
    @property
    def API_BASE_URL(cls):
        cls._load_config()
        return cls._CONFIG_DATA["api"].get("API_BASE_URL", "http://localhost:7989")

    @classmethod
    @property
    def POLL_INTERVAL(cls):
        cls._load_config()
        return int(cls._CONFIG_DATA["api"].get("POLL_INTERVAL", 60))

    @classmethod
    @property
    def TASK_TIMEOUT(cls):
        cls._load_config()
        return int(cls._CONFIG_DATA["api"].get("TASK_TIMEOUT", 300))

    # API Endpoints
    @staticmethod
    def get_tasks_endpoint():
        return f"{Config.API_BASE_URL}/machine/tasks"

    @staticmethod
    def update_task_status_endpoint():
        return f"{Config.API_BASE_URL}/tasks/status"


class USB_PIN:
    """Configuration for USB PINs mapped to company IDNOs"""

    @classmethod
    def get_pin(cls, person_name_certificate: str) -> str:
        """Get USB PIN for a company IDNO."""
        Config._load_config()
        pins = Config._CONFIG_DATA.get("pins", {})

        if person_name_certificate not in pins:
            raise IDNONotFoundException(person_name_certificate)

        pin = pins[person_name_certificate]

        if not pin:
            raise NoPinFoundException(f"No PIN found for {person_name_certificate}")

        return pin
