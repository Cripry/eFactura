from machine.domain.models.dataclass.dataclass import (
    Worker,
    Session,
)

from machine.domain.exceptions import LoginFailedException
import logging


class LoginService:
    def __init__(self, web_handler, desktop_handler):
        self.web_handler = web_handler
        self.desktop_handler = desktop_handler
        self.logger = logging.getLogger(__name__)

    def login_worker(self, worker: Worker) -> Session:
        self.logger.info(f"Starting login process for worker: {worker.my_company_idno}")
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
            self.web_handler.navigate_to_efactura(worker)

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
