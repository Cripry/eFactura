from enum import Enum
from typing import List, Dict
from machine.invoice_signer_ddd.domain.services.efactura_web_page import EfacturaWebPage
from machine.invoice_signer_ddd.domain.services.msign_web_page import MSignWebPage
from machine.invoice_signer_ddd.domain.models.urls import BuyerUrls
import logging


class BuyerRoleSelectors(Enum):
    """Selectors specific to buyer role"""

    pass


class BuyerRoleEfactura(EfacturaWebPage):
    """Implementation of eFactura web page for buyer role"""

    def __init__(self, worker, web_handler, desktop_handler):
        super().__init__(worker, web_handler)
        self.msign_service = MSignWebPage(web_handler, desktop_handler)
        self.logger = logging.getLogger(__name__)

    def sign_invoice(self, seria: str, number: str) -> bool:
        """Sign invoice as buyer"""
        self.logger.info(f"Starting invoice signing process for {seria}-{number}")

        try:
            # 1. Navigate to invoices to sign page
            self._navigate_to_invoices_to_sign()

            # 2. Find and select invoice
            if not self._find_and_select_invoice(seria, number):
                return False

            # 3. Initiate signing process
            if not self._complete_signing_process():
                return False

            return True
        except Exception as e:
            self.logger.error(f"Failed to sign invoice: {str(e)}")
            return False

    def _navigate_to_invoices_to_sign(self) -> None:
        """Navigate to invoices to sign page"""
        self.logger.info("Navigating to invoices to sign page")
        self.web_handler.navigate_to_url(
            f"{self.web_handler.efactura_base_url}{BuyerUrls.INVOICES_TO_SIGN.value}"
        )

    def _find_and_select_invoice(self, seria: str, number: str) -> bool:
        """Find and select invoice by seria and number"""
        self.logger.info(f"Searching for invoice {seria}-{number}")
        if not self.find_invoice_by_seria_and_number(seria, number):
            raise Exception("Invoice not found")

        if not self.select_invoice_checkbox():
            raise Exception("Failed to select invoice")

        return True

    def _complete_signing_process(self) -> bool:
        """Complete the signing process"""
        self.logger.info("Starting signing procedure")

        # 1. Start eFactura signing process
        if not self.start_signing_procedure():
            raise Exception("Failed to start signing procedure")

        # 2. Complete MSign signing
        if not self.msign_service.complete_signing(self.worker.idno, self.worker.pin):
            raise Exception("Failed to complete MSign signing")

        return True

    def sign_multiple_invoices(self, tasks: List[Dict[str, str]]) -> Dict[str, bool]:
        """Sign multiple invoices based on provided tasks"""
        self.logger.info(f"Starting to sign {len(tasks)} invoices")
        results = {}

        for task in tasks:
            seria = task.get("seria")
            number = task.get("number")

            if not seria or not number:
                self.logger.warning(f"Invalid task format: {task}")
                results[f"{seria}-{number}"] = False
                continue

            try:
                self.logger.info(f"Signing invoice {seria}-{number}")
                success = self.sign_invoice(seria, number)
                results[f"{seria}-{number}"] = success

                if not success:
                    self.logger.warning(f"Failed to sign invoice {seria}-{number}")

            except Exception as e:
                self.logger.error(f"Error signing invoice {seria}-{number}: {str(e)}")
                results[f"{seria}-{number}"] = False

        self.logger.info(f"Completed signing {len(tasks)} invoices")
        return results
