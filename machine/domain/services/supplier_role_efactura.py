import logging
import time
from typing import Optional

import pyperclip
from machine.domain.schemas import SignatureType
from machine.domain.models.navigation.urls import SupplierUrls
from machine.domain.services.efactura_web_page import EfacturaWebPage
from machine.domain.services.msign_web_page import MSignWebPage
from machine.infrastructure.selenium.selectors import (
    EFacturaSelectors,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


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

    def sign_all_invoices(
        self, company_idno: str, signature_type: SignatureType
    ) -> None:
        """Sign all invoices created by supplier"""
        self.logger.info("Starting to sign all invoices")

        # 1. Navigate to new invoices page
        self._navigate_to_new_invoices()

        # 2. Select all invoices
        self._select_buyer(company_idno)

        # 3. Apply first signature
        self._complete_signing_process(signature_type)

        # 4. Wait until all invoices are signed
        self._wait_until_all_invoices_signed()

        # 5. Navigate to  applied first signature page
        self._navigate_to_applyied_first_signature()

        # 5. Apply second signature
        self._complete_signing_process(signature_type)

        # 6. Wait until all invoices are signed
        self._wait_until_all_invoices_signed()

    def _navigate_to_new_invoices(self) -> None:
        """Navigate to new invoices page"""
        self.logger.info("Navigating to new invoices page")
        self.web_handler.navigate_to_url(
            f"{self.web_handler.efactura_base_url}{SupplierUrls.NEW_INVOICE.value}"
        )

    def _navigate_to_applyied_first_signature(self) -> None:
        """Navigate to applyied first signare page"""
        self.logger.info("Navigating to applyied first signare page")
        self.web_handler.navigate_to_url(
            f"{self.web_handler.efactura_base_url}{SupplierUrls.APPLYIED_FIRST_SIGNATURE.value}"
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

    def _select_buyer(self, company_idno: str) -> bool:
        """Select buyer from dropdown"""
        self.logger.info("Selecting buyer")

        try:
            buyer_input_field = self.web_handler.wait.wait_for_web_element_clickable(
                EFacturaSelectors.BUYER_INPUT_FIELD.value
            )

            buyer_input_field.click()

            time.sleep(1)

            action = ActionChains(self.web_handler.driver)

            pyperclip.copy(company_idno)  # Copy to clipboard
            action.key_down(Keys.CONTROL).send_keys("v").key_up(Keys.CONTROL).perform()

            time.sleep(1)

            # Select first input choise
            self.web_handler.wait.wait_for_web_element_clickable(
                EFacturaSelectors.BUYER_FIRST_INPUT_CHOISE.value
            ).click()

            # Click find company button
            self.web_handler.wait.wait_for_web_element_clickable(
                EFacturaSelectors.FIND_COMPANY_BUTTON.value
            ).click()

            time.sleep(1)

            self._select_all_invoices()

            return True
        except Exception as e:
            self.logger.error(f"Failed to select buyer: {str(e)}")
            return False

    def _wait_until_all_invoices_signed(self) -> None:
        """Wait until all invoices are signed"""
        self.logger.info("Waiting until all invoices are signed")

        # Then wait until we are redirected back to the main page
        self.logger.info("Waiting to be redirected back to the main page")
        self.web_handler.condition_handler.wait_until_url_matches_domain(
            self.web_handler.efactura_base_url
        )

        self.logger.info("Successfully completed signing process")

    def _complete_second_signature_signing_process(self) -> None:
        """Complete second signature signing process"""
        self.logger.info("Completing second signature signing process")

        # 1. Navigate to signed invoices page
        self._navigate_to_applyied_first_signature()

        # 2. Select all invoices
        self._select_all_invoices()

        # 3. Complete signing process
        self._complete_second_signature_signing_process()
