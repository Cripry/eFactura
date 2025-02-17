from selenium.webdriver.remote.webelement import WebElement
from machine.invoice_signer_ddd.domain.models.component_characteristics import (
    ComponentCharacteristics,
)
from machine.invoice_signer_ddd.infrastructure.selenium.selectors import MSignSelectors
from machine.invoice_signer_ddd.infrastructure.desktop.msign_handler import (
    MSignDesktopHandler,
)
import logging
import time


class MSignWebPage:
    """Service for handling MSign web page interactions"""

    def __init__(self, web_handler, desktop_handler: MSignDesktopHandler):
        self.web_handler = web_handler
        self.desktop_handler = desktop_handler
        self.logger = logging.getLogger(__name__)

    def _select_usb_sign_option(self) -> None:
        """Select the second USB signing option"""
        self.logger.info("Selecting USB signing option")
        auth_blocks = self.web_handler.wait.wait_for_web_elements(
            MSignSelectors.USB_SIGN_OPTION.value
        )

        if len(auth_blocks) < 2:
            raise Exception(
                f"Expected at least 2 authentication blocks, found {len(auth_blocks)}"
            )

        # Select the second authentication block
        usb_option = auth_blocks[1]
        self._scroll_and_click(usb_option)

    def _find_certificate_card(self, idno: str) -> WebElement:
        """Find certificate card by IDNO"""
        self.logger.info(f"Looking for certificate card with IDNO: {idno}")
        certificate_cards = self.web_handler.wait.wait_for_web_elements(
            MSignSelectors.CERTIFICATE_CARDS.value
        )

        for card in certificate_cards:
            if idno in card.text:
                self.logger.info(f"Found certificate card with IDNO {idno}")
                return card

        raise Exception(f"Certificate card with IDNO {idno} not found")

    def _click_sign_button(self, card: WebElement) -> None:
        """Click sign button within a certificate card"""
        self.logger.info("Clicking sign button...")
        sign_button = card.find_element(*MSignSelectors.SIGN_BUTTON.value)
        self._scroll_and_click(sign_button)

    def _scroll_and_click(self, element: WebElement) -> None:
        """Scroll element into view and click it"""
        self.web_handler.driver.execute_script(
            "arguments[0].scrollIntoView(true);", element
        )
        time.sleep(0.5)
        element.click()

    def complete_signing(self, idno: str, pin: str) -> bool:
        """Complete the signing process on MSign website"""
        self.logger.info("Starting MSign signing process")
        try:
            # Wait for navigation to MSign sign page
            self.logger.info("Waiting for confirmation navigation to MSign sign page")
            self.web_handler.condition_handler.wait_for_characteristics(
                ComponentCharacteristics.MSIGN_SIGN_PAGE
            )

            # 1. Select USB signing option
            self._select_usb_sign_option()

            # 2. Find and select certificate
            certificate_card = self._find_certificate_card(idno)

            # 3. Initiate signing
            self._click_sign_button(certificate_card)

            # 4. Handle MSign desktop app interaction
            self.logger.info("Handling MSign desktop interaction...")
            self.desktop_handler.input_pin(pin)
            self.logger.info("MSign signing process completed")
            time.sleep(6)  # Wait for signing to complete

            return True

        except Exception as e:
            self.logger.error(f"Failed to complete MSign signing: {str(e)}")
            return False
