from machine.invoice_signer_ddd.domain.models.navigation.urls import CompanyUrls
from machine.invoice_signer_ddd.domain.models.auth import Worker
from machine.invoice_signer_ddd.domain.events.navigation_events import (
    NavigationStarted,
    NavigationCompleted,
    NavigationFailed,
)
import logging


class NavigationService:
    def __init__(self, web_handler):
        self.web_handler = web_handler
        self.logger = logging.getLogger(__name__)

    def navigate_to_efactura(self, worker: Worker) -> None:
        try:
            NavigationStarted(destination="e-Factura")
            self.logger.info("Navigating to companies list page")
            self.web_handler.navigate_to_url(
                CompanyUrls.get_url(self.web_handler.environment)
            )
            # ... rest of the navigation logic ...
            NavigationCompleted(destination="e-Factura")
        except Exception as e:
            self.logger.error(f"Navigation failed: {str(e)}")
            NavigationFailed(destination="e-Factura", reason=str(e))
            raise
