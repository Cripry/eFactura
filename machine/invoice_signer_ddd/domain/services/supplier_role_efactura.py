from enum import Enum
import logging
from typing import Optional
from machine.invoice_signer_ddd.domain.models.urls import SupplierUrls
from machine.invoice_signer_ddd.domain.services.efactura_web_page import EfacturaWebPage
from machine.invoice_signer_ddd.domain.services.msign_web_page import MSignWebPage
from machine.invoice_signer_ddd.infrastructure.selenium.selectors import (
    EFacturaSelectors,
)


class SupplierRoleSelectors(Enum):
    """Selectors specific to supplier role"""

    pass


class SupplierRoleEfactura(EfacturaWebPage):
    """Implementation of eFactura web page for supplier role"""

    def __init__(self, worker, web_handler, desktop_handler):
        super().__init__(worker, web_handler)
        self.msign_service = MSignWebPage(web_handler, desktop_handler)
        self.logger = logging.getLogger(__name__)

    def navigate_to_section(self, section_name: str) -> bool:
        """Supplier-specific section navigation"""
        raise NotImplementedError

    def perform_action(self, action_name: str, *args) -> Optional[bool]:
        """Supplier-specific actions"""
        raise NotImplementedError

    def sign_all_invoices(self) -> bool:
        """Sign all invoices created by supplier"""
        self.logger.info("Starting to sign all invoices")

        try:
            # 1. Navigate to new invoices page
            self._navigate_to_new_invoices()

            # 2. Select all invoices
            if not self._select_all_invoices():
                return False

            # 3. Complete signing process
            return self._complete_signing_process()

        except Exception as e:
            self.logger.error(f"Failed to sign all invoices: {str(e)}")
            return False

    def _navigate_to_new_invoices(self) -> None:
        """Navigate to new invoices page"""
        self.logger.info("Navigating to new invoices page")
        self.web_handler.navigate_to_url(
            f"{self.web_handler.efactura_base_url}{SupplierUrls.NEW_INVOICE.value}"
        )

    def _select_all_invoices(self) -> bool:
        """Select all invoices in the list"""
        self.logger.info("Selecting all invoices")

        try:
            select_all_checkbox = self.web_handler.wait.wait_for_web_element_clickable(
                EFacturaSelectors.SELECT_ALL_CHECKBOX.value
            )

            if not select_all_checkbox.is_selected():
                self._click_checkbox(select_all_checkbox)
                self.logger.info("All invoices selected")
                return True

            return False
        except Exception as e:
            self.logger.error(f"Failed to select all invoices: {str(e)}")
            return False
