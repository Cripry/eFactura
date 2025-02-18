import pyautogui
from pywinauto.application import Application
from pywinauto.timings import TimeoutError
from machine.domain.models.image_paths import ImagePaths
from machine.domain.exceptions import USBNotFoundException
import logging
import time
import cv2
import numpy as np
from PIL import ImageGrab
import os


class MSignDesktopHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.timeout = 30  # Maximum wait time in seconds

    def connect_to_running_app(self) -> None:
        """Connect to running MSign instance with timeout"""
        start_time = time.time()
        last_error = None

        while time.time() - start_time < self.timeout:
            try:
                self.app = Application(backend="uia").connect(
                    title="Introduceți noul cod PIN"
                )
                self.logger.info("Successfully connected to MSign application")
                return
            except Exception as e:
                last_error = str(e)
                self.logger.info(
                    f"Waiting for MSign window to appear... ({int(time.time() - start_time)}s)"
                )
                time.sleep(1)

        raise TimeoutError(
            f"Could not connect to MSign PIN window after {self.timeout} seconds. Last error: {last_error}"
        )

    def find_element_by_image(
        self,
        image_path: str,
        element_name: str,
        max_retries: int = 5,
        retry_interval: int = 2,
    ) -> tuple:
        """Find element on screen using template matching with retries"""
        for attempt in range(max_retries):
            try:
                # Verify image path exists
                if not os.path.exists(image_path):
                    raise FileNotFoundError(f"Image file not found at: {image_path}")

                template = cv2.imread(image_path)
                if template is None:
                    raise FileNotFoundError(
                        f"Could not load template image: {image_path}"
                    )

                screen = np.array(ImageGrab.grab())
                screen_bgr = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

                result = cv2.matchTemplate(screen_bgr, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                if max_val >= 0.8:  # Threshold for matching
                    return template, max_loc

                if attempt < max_retries - 1:
                    self.logger.info(
                        f"Attempt {attempt + 1}: {element_name} not found, retrying in {retry_interval} seconds..."
                    )
                    time.sleep(retry_interval)

            except Exception as e:
                if attempt < max_retries - 1:
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}, retrying in {retry_interval} seconds..."
                    )
                    time.sleep(retry_interval)
                else:
                    raise e

        raise USBNotFoundException(
            f"Could not find {element_name} after {max_retries} attempts"
        )

    def find_pin_field_location(self) -> tuple:
        """Find PIN input field location based on label image with retries"""
        try:
            template, max_loc = self.find_element_by_image(
                ImagePaths.PIN_FIELD.value, "PIN input field"
            )

            label_width = template.shape[1]
            label_height = template.shape[0]

            input_x = max_loc[0] + label_width + (label_width // 2)
            input_y = max_loc[1] + (label_height // 2)

            return input_x, input_y
        except Exception as e:
            raise USBNotFoundException(f"Failed to find PIN field location: {str(e)}")

    def find_ok_button_location(self) -> tuple:
        """Find OK button location based on button image with retries"""
        try:
            template, max_loc = self.find_element_by_image(
                ImagePaths.OK_BUTTON.value, "OK button"
            )

            # Calculate button center position
            button_width = template.shape[1]
            button_height = template.shape[0]

            # OK button is one full image width to the left of the found image
            # and vertically centered
            button_x = max_loc[0] - button_width  # Move left by full image width
            button_y = max_loc[1] + (button_height // 2)  # Vertically centered

            return button_x, button_y
        except Exception as e:
            raise USBNotFoundException(f"Failed to find OK button location: {str(e)}")

    def input_pin(self, pin: str) -> bool:
        """Handle PIN input in MSign window"""
        try:
            self.connect_to_running_app()
            self.logger.info("Connected to MSign application")

            self.app.window(title="Introduceți noul cod PIN")
            self.logger.info("PIN window found")

            input_x, input_y = self.find_pin_field_location()
            self.logger.info(f"Found PIN field at coordinates: ({input_x}, {input_y})")

            pyautogui.click(input_x, input_y)
            pyautogui.write(pin)
            self.logger.info("PIN entered")

            button_x, button_y = self.find_ok_button_location()
            self.logger.info(
                f"Found OK button at coordinates: ({button_x}, {button_y})"
            )
            pyautogui.click(button_x, button_y)
            self.logger.info("OK button clicked")

            return True
        except Exception as e:
            self.logger.error(f"Failed to handle MSign PIN input: {str(e)}")
            raise USBNotFoundException(str(e))
