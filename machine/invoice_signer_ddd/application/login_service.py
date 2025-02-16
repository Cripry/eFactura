from machine.invoice_signer_ddd.domain.models.worker import Worker
from machine.invoice_signer_ddd.domain.models.session import Session
from machine.invoice_signer_ddd.domain.exceptions import LoginFailedException
import logging
from machine.invoice_signer_ddd.infrastructure.selenium.selectors import (
    EFacturaSelectors,
)


class LoginService:
    def __init__(self, web_handler, desktop_handler, navigation_service):
        self.web_handler = web_handler
        self.desktop_handler = desktop_handler
        self.navigation_service = navigation_service
        self.logger = logging.getLogger(__name__)

    def login_worker(self, worker: Worker) -> Session:
        self.logger.info(f"Starting login process for worker: {worker.idno}")
        try:
            # Perform web-based operations
            self.logger.info("Performing web-based authentication")
            session = self.web_handler.authenticate_and_select_certificate(worker)

            # Perform desktop-based PIN input
            self.logger.info("Performing desktop-based PIN input")
            self.desktop_handler.input_pin(worker.pin)

            # Complete company and role selection
            self.logger.info("Performing company and role selection")
            self.web_handler.select_company_and_role(worker)

            # Navigate to e-Factura
            self.logger.info("Navigating to e-Factura platform")
            self.navigation_service.navigate_to_efactura(
                worker, self.web_handler.driver
            )

            # Check for and close any popups
            self.logger.info("Checking for popups...")
            self.close_popup_if_exists()

            self.logger.info("Login process completed successfully")
            return session
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            raise LoginFailedException(str(e))

    def logout_worker(self, session: Session) -> bool:
        """Handle worker logout process"""
        return self.auth_service.logout(session)

    def is_logged_in(self, session: Session) -> bool:
        return self.auth_service.validate_session(session)

    def close_popup_if_exists(self, timeout: int = 6) -> None:
        """
        Attempt to close any popup that might be present on the page.

        This method will:
        1. Look for a popup close button using selector from EFacturaSelectors
        2. If not found immediately, retry after specified timeout
        3. If found, click the button to close the popup
        4. If not found after retry, continue without error

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
