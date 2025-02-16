from machine.invoice_signer_ddd.domain.models.auth import Worker, Session
from machine.invoice_signer_ddd.domain.services.authentication_service import (
    AuthenticationService,
)
import logging


class AuthenticateUserUseCase:
    def __init__(self, auth_service: AuthenticationService):
        self.auth_service = auth_service
        self.logger = logging.getLogger(__name__)

    def execute(self, worker: Worker) -> Session:
        self.logger.info(f"Authenticating user: {worker.idno}")
        return self.auth_service.authenticate(worker)
