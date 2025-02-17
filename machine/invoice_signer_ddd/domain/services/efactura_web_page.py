from typing import Optional
from machine.invoice_signer_ddd.domain.models.worker import Worker
from selenium.webdriver.common.by import By
import time
import logging
from machine.invoice_signer_ddd.infrastructure.selenium.selectors import (
    EFacturaSelectors,
)
from selenium.webdriver.remote.webelement import WebElement
from machine.invoice_signer_ddd.domain.models.component_characteristics import (
    ComponentCharacteristics,
)


class EfacturaWebPage:
    """Base class for eFactura web page interaction"""

    def __init__(self, worker: Worker, web_handler):
        self.worker = worker
        self.web_handler = web_handler
        self.logger = logging.getLogger(__name__)

    def navigate_to_section(self, section_name: str) -> bool:
        """Navigate to specific section of eFactura"""
        raise NotImplementedError

    def perform_action(self, action_name: str, *args) -> Optional[bool]:
        """Perform generic action on eFactura page"""
        raise NotImplementedError

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

    def start_signing_procedure(self) -> bool:
        """Start the signing procedure for selected invoices"""
        self.logger.info("Starting signing procedure")

        try:
            # 1. Click start sign button
            self.logger.info("Clicking start sign button")
            start_sign_button = self.web_handler.wait.wait_for_web_element_clickable(
                EFacturaSelectors.START_SIGN_BUTTON.value
            )
            start_sign_button.click()

            # 2. Wait for confirmation popup
            self.logger.info("Waiting for confirmation popup")
            self.web_handler.condition_handler.wait_for_characteristics(
                ComponentCharacteristics.SIGN_CONFIRMATION_POPUP
            )

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

    def _complete_signing_process(self) -> bool:
        """Complete the signing process (common for both roles)"""
        self.logger.info("Starting signing procedure")

        # 1. Start eFactura signing process
        if not self.start_signing_procedure():
            raise Exception("Failed to start signing procedure")

        # 2. Complete MSign signing
        if not self.msign_service.complete_signing(self.worker.idno, self.worker.pin):
            raise Exception("Failed to complete MSign signing")

        return True
