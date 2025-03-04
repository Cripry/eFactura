from typing import Optional, Union

from machine.domain.schemas import SignatureType
from machine.domain.models.dataclass.dataclass import Worker
from selenium.webdriver.common.by import By
import time
import logging
from machine.infrastructure.selenium.selectors import (
    EFacturaSelectors,
)
from selenium.webdriver.remote.webelement import WebElement
from machine.domain.models.selectors.component_characteristics import (
    ComponentCharacteristics,
)


class EfacturaWebPage:
    """Base class for eFactura web page interaction"""

    def __init__(self, worker: Worker, web_handler):
        self.worker = worker
        self.web_handler = web_handler
        self.logger = logging.getLogger(__name__)

    def find_invoice_by_seria_and_number(self, seria: str, number: str) -> bool:
        """Find invoice by seria and number"""
        self.logger.info(f"Searching for invoice {seria}-{number}")

        try:
            # 1. Fill seria field
            seria_input = self.web_handler.wait.wait_for_web_element_clickable(
                EFacturaSelectors.SERIA_INPUT.value
            )
            seria_input.click()
            seria_input.clear()
            seria_input.send_keys(seria)

            # 2. Fill number field
            number_input = self.web_handler.wait.wait_for_web_element_clickable(
                EFacturaSelectors.NUMBER_INPUT.value
            )
            number_input.click()
            number_input.clear()
            number_input.send_keys(number)

            # 3. Click search button
            search_button = self.web_handler.wait.wait_for_web_element_clickable(
                EFacturaSelectors.SEARCH_BUTTON.value
            )
            search_button.click()

            return True
        except Exception as e:
            self.logger.error(f"Failed to find invoice: {str(e)}")
            return False

    def select_invoice_checkbox(self) -> bool:
        """Select invoice checkbox in the results table"""
        self.logger.info("Selecting invoice checkbox")

        try:
            max_retries = 3
            checkbox_found = False

            for attempt in range(max_retries):
                try:
                    # Wait for table to be present and get fresh reference
                    self.web_handler.wait.wait_for_web_element(
                        EFacturaSelectors.INVOICE_TABLE.value
                    )
                    time.sleep(1)  # Short pause to let table fully load

                    # Get fresh rows
                    rows = self.web_handler.wait.wait_for_web_elements(
                        (By.CLASS_NAME, "row")
                    )

                    if not rows:
                        raise Exception(
                            "No invoices found matching the search criteria"
                        )

                    # Find and check the invoice checkbox
                    for row in rows:
                        try:
                            checkbox = self._find_checkbox_in_row(row)
                            if checkbox:
                                self._click_checkbox(checkbox)
                                checkbox_found = True
                                self.logger.info("Invoice checkbox checked")
                                break

                        except Exception as e:
                            self.logger.error(f"Error processing row: {str(e)}")
                            continue

                    if checkbox_found:
                        break  # Exit retry loop if checkbox was found and clicked

                except Exception as e:
                    if attempt == max_retries - 1:  # Last attempt
                        raise Exception(
                            f"Failed to process table after {max_retries} attempts: {str(e)}"
                        )
                    self.logger.info(f"Attempt {attempt + 1} failed, retrying...")
                    time.sleep(1)
                    continue

            return checkbox_found

        except Exception as e:
            self.logger.error(f"Failed to select invoice checkbox: {str(e)}")
            return False

    def _find_checkbox_in_row(self, row) -> Optional[WebElement]:
        """Find checkbox element within a row"""
        try:
            return row.find_element(By.XPATH, ".//input[@type='checkbox']")
        except Exception:
            return None

    def _click_checkbox(self, checkbox: WebElement) -> None:
        """Click on a checkbox element with proper handling"""
        try:
            if not checkbox.is_selected():
                # Scroll into view before clicking
                self.web_handler.driver.execute_script(
                    "arguments[0].scrollIntoView(true);", checkbox
                )
                time.sleep(0.5)

                # Try to click with JavaScript if regular click fails
                try:
                    checkbox.click()
                except Exception:
                    self.web_handler.driver.execute_script(
                        "arguments[0].click();", checkbox
                    )
        except Exception as e:
            self.logger.error(f"Failed to click checkbox: {str(e)}")
            raise

    def start_signing_procedure(
        self, start_sign_button_selector, signature_type: Union[SignatureType, None] = None
    ) -> bool:
        """Start the signing procedure for selected invoices"""
        self.logger.info("Starting signing procedure")

        try:
            # 1. Click start sign button
            self.logger.info("Clicking start sign button")
            start_sign_button = self.web_handler.wait.wait_for_web_element_clickable(
                start_sign_button_selector
            )
            start_sign_button.click()

            # 2. Wait for confirmation popup
            self.logger.info("Waiting for confirmation popup")
            self.web_handler.condition_handler.wait_for_characteristics(
                ComponentCharacteristics.SIGN_CONFIRMATION_POPUP
            )

            if signature_type == SignatureType.SHORT:
                self.web_handler.wait.wait_for_web_element_clickable(
                    EFacturaSelectors.SHORT_RADIO_BUTTON.value
                ).click()
            elif signature_type == SignatureType.LONG:
                self.web_handler.wait.wait_for_web_element_clickable(
                    EFacturaSelectors.LONG_RADIO_BUTTON.value
                ).click()

            time.sleep(2)

            # 3. Click final sign button
            self.logger.info("Clicking final sign button")
            final_sign_button = self.web_handler.wait.wait_for_web_element_clickable(
                EFacturaSelectors.FINAL_SIGN_BUTTON.value
            )
            final_sign_button.click()

            self.logger.info("Signing procedure completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start signing procedure: {str(e)}")
            return False


    def close_popup_if_exists(self, timeout: int = 6) -> None:
        """
        Attempt to close any popup that might be present on the page.

        Args:
            timeout: Time in seconds to wait for popup to appear (default: 6)
        """
        self.logger.info(f"Checking for popup with timeout: {timeout} seconds...")
        try:
            # Try to find the popup close button with custom timeout
            close_button = self.web_handler.wait.wait_for_web_element_clickable(
                EFacturaSelectors.POPUP_CLOSE_BUTTON.value, timeout=timeout
            )

            if close_button:
                self.logger.info("Popup found - closing it")
                close_button.click()
                self.logger.info("Popup closed successfully")
            else:
                self.logger.info("No popup found")

        except Exception as e:
            self.logger.debug(f"No popup found or could not close: {str(e)}")
            # Continue execution even if popup not found
            pass
