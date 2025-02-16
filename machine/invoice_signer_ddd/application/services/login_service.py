from machine.invoice_signer_ddd.domain.models.auth import Worker, Session
from machine.invoice_signer_ddd.domain.services.auth import AuthenticationService
from machine.invoice_signer_ddd.domain.services.navigation import NavigationService
from machine.invoice_signer_ddd.domain.events.auth_events import UserAuthenticated, AuthenticationFailed
import logging

class LoginService:
    def __init__(self, auth_service: AuthenticationService, navigation_service: NavigationService):
        self.auth_service = auth_service
        self.navigation_service = navigation_service
        self.logger = logging.getLogger(__name__)

    def login_worker(self, worker: Worker) -> Session:
        self.logger.info(f"Starting login process for worker: {worker.idno}")
        try:
            # Authentication
            session = self.auth_service.authenticate(worker)
            UserAuthenticated(user_id=worker.idno)
            
            # Navigation
            self.navigation_service.navigate_to_efactura(worker)
            
            self.logger.info("Login process completed successfully")
            return session
        except Exception as e:
            self.logger.error(f"Login failed: {str(e)}")
            AuthenticationFailed(user_id=worker.idno, reason=str(e))
            raise 