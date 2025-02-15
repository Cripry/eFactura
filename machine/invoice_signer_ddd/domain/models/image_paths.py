from enum import Enum
import os


def get_project_root():
    """Get the absolute path to the project root directory"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ImagePaths(Enum):
    PIN_FIELD = os.path.join(
        get_project_root(), "resources", "images", "introduceti_pin_field.png"
    )
    OK_BUTTON = os.path.join(
        get_project_root(), "resources", "images", "ok_pin_button.png"
    )
