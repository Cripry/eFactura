from machine.invoice_signer_ddd.domain.models.auth import Worker
from machine.invoice_signer_ddd.domain.services.auth import CertificateService
from machine.invoice_signer_ddd.domain.events.auth_events import CertificateSelected
import logging

class SelectCertificateUseCase:
    def __init__(self, certificate_service: CertificateService):
        self.certificate_service = certificate_service
        self.logger = logging.getLogger(__name__)

    def execute(self, worker: Worker) -> CertificateSelected:
        self.logger.info(f"Selecting certificate for user: {worker.idno}")
        try:
            certificate = self.certificate_service.select_certificate(worker)
            return CertificateSelected(user_id=worker.idno)
        except Exception as e:
            self.logger.error(f"Certificate selection failed: {str(e)}")
            raise 