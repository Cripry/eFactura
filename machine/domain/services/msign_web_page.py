from selenium.webdriver.remote.webelement import WebElement
from machine.domain.models.selectors.component_characteristics import (
    ComponentCharacteristics,
)
from machine.infrastructure.selenium.selectors import MSignSelectors
from machine.infrastructure.desktop.msign_handler import (
    MSignDesktopHandler,
)
import logging
import time


def is_name_contained(search_term: str, text: str) -> bool:
    """
    Check if all parts of the search_term (first, middle, last names) are contained in the text.

    :param search_term: The name to search for (can be in any order or case)
    :param text: The text in which to search
    :return: True if all parts of the name are found in the text, False otherwise
    """
    search_term = search_term.upper().strip()  # Normalize search term
    text = text.upper().strip()  # Normalize text

    name_parts = search_term.split()  # Split search term into parts

    # Check if all parts of the name exist in the text
    for part in name_parts:
        if part not in text:
            return False

    return True  # All parts were found in the text


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

    def _find_certificate_card(self, person_name_certificate: str) -> WebElement:
        """Find certificate card by my_company_idno"""
        self.logger.info(
            f"Looking for certificate card with my_company_idno: {person_name_certificate}"
        )
        certificate_cards = self.web_handler.wait.wait_for_web_elements(
            MSignSelectors.CERTIFICATE_CARDS.value
        )

        for card in certificate_cards:
            if is_name_contained(person_name_certificate, card.text):
                self.logger.info(
                    f"Found certificate card with my_company_idno {person_name_certificate}"
                )
                return card

        raise Exception(
            f"Certificate card with my_company_idno {person_name_certificate} not found"
        )

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

    def complete_signing(self, person_name_certificate: str, pin: str) -> bool:
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
            certificate_card = self._find_certificate_card(person_name_certificate)

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
