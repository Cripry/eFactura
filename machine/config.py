import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SERVER_URL = os.getenv("SERVER_URL", "http://localhost:7989")
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", 60))  # in seconds
    TASK_TIMEOUT = int(os.getenv("TASK_TIMEOUT", 300))  # in seconds
    USB_TIMEOUT = int(os.getenv("USB_TIMEOUT", 10))  # in seconds

    # API Endpoints
    @staticmethod
    def get_tasks_endpoint():
        return f"{Config.SERVER_URL}/machine/tasks"

    @staticmethod
    def update_task_status_endpoint():
        return f"{Config.SERVER_URL}/tasks/status"
