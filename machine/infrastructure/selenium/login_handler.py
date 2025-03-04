from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from machine.domain.models.dataclass.dataclass import Worker, Session
from machine.infrastructure.selenium.selectors import (
    LoginPageSelectors,
    SFSSelectors,
)
from machine.domain.exceptions import CertificateNotFoundException
from machine.infrastructure.selenium.wait_helper import (
    WaitHelper,
)
from machine.domain.models.selectors.component_characteristics import (
    ComponentCharacteristics,
)
from machine.infrastructure.selenium.wait_condition_handler import (
    WaitConditionHandler,
)
import logging
import time
from selenium.webdriver.support.select import Select
from machine.domain.models.navigation.urls import (
    EfacturaBaseUrls,
    SFSBaseUrls,
    CompanyUrls,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui


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


class SeleniumLoginHandler:
    def __init__(self, driver: WebDriver, environment: str):
        self.driver = driver
        self.environment = environment
        self.sfs_base_url = SFSBaseUrls.get_base_url(environment)
        self.efactura_base_url = EfacturaBaseUrls.get_base_url(environment)
        self.wait = WaitHelper(self.driver, 10)
        self.condition_handler = WaitConditionHandler(self.driver)
        self.logger = logging.getLogger(__name__)

    def navigate_to_sfs(self) -> None:
        self.logger.info(f"Navigating to SFS portal: {self.sfs_base_url}")
        self.driver.get(self.sfs_base_url)

    def click_cabinet_button(self) -> None:
        self.logger.debug("Clicking cabinet button")
        element = self.driver.find_element(
            *LoginPageSelectors.LOGIN_INITIAL_BUTTON.value
        )
        element.click()

    def click_mpass_option(self) -> None:
        self.logger.debug("Clicking mPass option")
        element = self.driver.find_element(*LoginPageSelectors.LOGIN_MPASS_BUTTON.value)
        element.click()

    def click_usb_sign_option(self) -> None:
        self.logger.debug("Clicking USB sign option")
        element = self.driver.find_element(*LoginPageSelectors.LOGIN_MSIGN_BUTTON.value)
        element.click()

    def select_certificate(self, person_name_certificate: str) -> bool:
        self.logger.info(
            f"Selecting certificate for person_name_certificate: {person_name_certificate}"
        )

        try:
            # Wait for certificate page to load
            self.condition_handler.wait_for_characteristics(
                ComponentCharacteristics.CERTIFICATE_PAGE
            )

            # Remove debug bar
            self._remove_debug_bar()

            container = self.driver.find_element(
                *LoginPageSelectors.CERTIFICATES_CONTAINER.value
            )
            certificates = container.find_elements(By.TAG_NAME, "button")

            for cert in certificates:
                if is_name_contained(person_name_certificate, cert.text):
                    self.logger.debug(f"Found matching certificate: {cert.text}")
                    cert.click()
                    return True

            raise CertificateNotFoundException(person_name_certificate)
        except Exception as e:
            self.logger.error(f"Certificate selection failed: {str(e)}")
            raise

    def authenticate_and_select_certificate(self, worker: Worker) -> Session:
        """Handle web-based authentication and certificate selection"""
        self.logger.info("Starting web-based authentication and certificate selection")
        try:
            # Navigate and authenticate
            self.navigate_to_sfs()
            self.click_cabinet_button()
            self.click_mpass_option()
            self.click_usb_sign_option()

            # Select certificate
            self.select_certificate(worker.person_name_certificate)

            self.logger.info("Web authentication and certificate selection completed")
            return Session(
                my_company_idno=worker.my_company_idno,
                person_name_certificate=worker.person_name_certificate,
            )
        except Exception as e:
            self.logger.error(f"Web authentication failed: {str(e)}")
            raise Exception(f"Web authentication failed: {str(e)}")

    def _find_and_select_company(self, worker: Worker) -> bool:
        """Helper method to find and select company with dynamic loading"""
        self.logger.debug("Starting dynamic company search")

        seen_companies = set()  # Track all seen companies
        no_new_companies_count = 0  # Counter for consecutive no-new-companies
        max_no_new_companies = 4  # Max attempts with no new companies

        # Get the companies container once
        companies_container = self.wait.wait_for_web_element(
            LoginPageSelectors.COMPANIES_LIST.value
        )

        # Create ActionChains instance for mouse actions
        actions = ActionChains(self.driver)

        # 1. Scroll entire page by 30% of page height
        page_height = self.driver.execute_script("return window.innerHeight")
        scroll_amount = int(page_height * 0.3)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(0.5)

        # 2. Hover to the first company element from the container
        # First wait for companies to be present in the container
        self.wait.wait_for_web_elements(LoginPageSelectors.COMPANY_ITEMS.value)
        # Then find the first company within the container
        first_company = companies_container.find_element(
            *LoginPageSelectors.COMPANY_ITEMS.value
        )
        actions.move_to_element(first_company).perform()
        time.sleep(0.5)

        while no_new_companies_count < max_no_new_companies:
            # Get current list of companies within the container
            current_companies = companies_container.find_elements(
                *LoginPageSelectors.COMPANY_ITEMS.value
            )

            # Track if we found new companies in this iteration
            found_new = False

            for company in current_companies:
                company_text = company.text

                # Skip if we've already seen this company
                if company_text in seen_companies:
                    continue

                # Add to seen companies
                seen_companies.add(company_text)
                found_new = True

                # Check if this is our target company
                if worker.my_company_idno in company_text:
                    self.logger.info(
                        f"Found company with my_company_idno {worker.my_company_idno}"
                    )
                    company.click()
                    return True

            # If no new companies were found, increment counter
            if not found_new:
                no_new_companies_count += 1
            else:
                no_new_companies_count = 0  # Reset counter if we found new companies

            # 3. Scroll within the container using pyautogui
            if current_companies:
                # Get dropdown area element using Selenium
                dropdown_area = self.driver.find_element(
                    *LoginPageSelectors.SELECT_AREA_DROPDOWN.value
                )

                # Move mouse to the center of the dropdown area
                location = dropdown_area.location
                size = dropdown_area.size
                center_x = location["x"] + (size["width"] / 2)
                center_y = location["y"] + (size["height"] / 2)

                # Move mouse to the center position
                pyautogui.moveTo(center_x, center_y, duration=0.5)

                # Simulate mouse wheel scroll
                pyautogui.scroll(-200)  # Negative value scrolls down
                time.sleep(1)  # Wait for new companies to load

        return False

    def select_company_and_role(self, worker: Worker) -> None:
        """Select company and role after successful authentication"""
        self.logger.info("Starting company and role selection")
        try:
            # 1. Select juridic person type
            self.logger.debug("Selecting person type...")
            person_type_select = self.wait.wait_for_web_element(
                LoginPageSelectors.PERSON_TYPE_SELECT.value
            )
            self._remove_debug_bar()

            select = Select(person_type_select)
            select.select_by_value("juridic")
            time.sleep(1)

            # 2. Select company
            self.logger.debug("Selecting company...")
            company_dropdown = self.wait.wait_for_web_element_clickable(
                LoginPageSelectors.COMPANY_DROPDOWN.value
            )
            company_dropdown.click()
            time.sleep(2)

            # Use new dynamic company search method
            if not self._find_and_select_company(worker):
                raise Exception(
                    f"Company with my_company_idno {worker.my_company_idno} not found"
                )

            time.sleep(1)

            # 3. Select role
            self.logger.debug("Selecting role...")
            role_dropdown = self.wait.wait_for_web_element_clickable(
                LoginPageSelectors.ROLE_DROPDOWN.value
            )
            role_dropdown.click()
            time.sleep(1)

            # Find role
            roles = self.driver.find_elements(*LoginPageSelectors.ROLE_ITEMS.value)
            role_found = False
            for role in roles:
                if worker.role in role.text:
                    self.logger.info(f"Found role: {worker.role}")
                    role.click()
                    role_found = True
                    break

            if not role_found:
                raise Exception(f"Role {worker.role} not found")

            # 4. Click Set button
            self.logger.debug("Clicking Set button...")
            set_button = self.wait.wait_for_web_element_clickable(
                LoginPageSelectors.SET_BUTTON.value
            )
            set_button.click()
            self.logger.info("Company and role selection completed")

        except Exception as e:
            error_msg = str(e).replace(
                "Object of type WebDriver is not JSON serializable",
                "WebDriver operation failed",
            )
            self.logger.error(f"Failed to select company and role: {error_msg}")
            raise Exception(f"Company and role selection failed: {error_msg}")

    def navigate_to_login(self, url: str) -> None:
        self.driver.get(url)

    def navigate_to_url(
        self, url, max_retries=30, timeout=8, retry_until_success=False
    ):
        """
        Navigate to a URL with optional retry mechanism
        Args:
            url: URL to navigate to
            max_retries: Maximum number of retry attempts (default: 30)
            timeout: Time to wait between retries in seconds (default: 3)
            retry_until_success: If True, retry navigation until URL matches (default: False)
        """
        print(f"Navigating to: {url}")
        self.driver.get(url)

        if retry_until_success:
            current_url = self.driver.current_url
            retry_count = 0

            while url not in current_url and retry_count < max_retries:
                print(f"Navigation to {url} failed. Current URL: {current_url}")
                self.driver.get(url)
                time.sleep(timeout)
                current_url = self.driver.current_url
                retry_count += 1

            if url not in current_url:
                raise Exception(
                    f"Failed to navigate to {url}. Current URL: {current_url}"
                )

            print(f"Successfully navigated to: {current_url}")

        time.sleep(timeout)  # Wait for page to load completely

    def _remove_debug_bar(self):
        """Remove PHP debug bar if it exists"""
        try:
            time.sleep(1)
            debug_bar = self.driver.find_element(By.CLASS_NAME, "phpdebugbar")
            if debug_bar:
                self.driver.execute_script(
                    "var debugBar = document.querySelector('.phpdebugbar'); "
                    "if(debugBar) { debugBar.remove(); }"
                )
                print("Debug bar removed")
        except Exception:
            pass  # Debug bar not found, continue normally

    def navigate_to_efactura(self, worker: Worker) -> None:
        """Navigate to e-factura platform and select company"""
        self.logger.info("Navigating to e-Factura platform")
        try:
            # Use sfs_base_url for initial navigation
            self.navigate_to_url(
                CompanyUrls.get_url(self.environment),
                retry_until_success=True,
            )

            # Remove debug bar
            self._remove_debug_bar()

            # Find and select company
            target_row = self._find_company_row_by_my_company_idno(
                worker.my_company_idno
            )
            self._click_administration_button(target_row)

            # Remove debug bar
            self._remove_debug_bar()

            # Handle e-Factura block
            self._find_and_click_efactura_block()

            # Handle window switching
            self._switch_to_efactura_window()

            self.logger.info("Successfully navigated to e-Factura")
            time.sleep(2)  # Wait for page to load

        except Exception as e:
            self.logger.error(f"Failed to navigate to e-factura platform: {str(e)}")
            raise Exception(f"Navigation to e-Factura failed: {str(e)}")

    def _find_company_row_by_my_company_idno(self, my_company_idno: str) -> WebElement:
        """Find company row by my_company_idno"""
        self.logger.info(
            f"Searching for company with my_company_idno: {my_company_idno}"
        )
        company_rows = self.wait.wait_for_web_elements(
            SFSSelectors.COMPANY_GRID_ITEM.value
        )

        if not company_rows:
            raise Exception("No company rows found on the page")

        for row in company_rows:
            try:
                my_company_idno_span = row.find_element(
                    *SFSSelectors.COMPANY_my_company_idno.value
                )
                if my_company_idno in my_company_idno_span.text:
                    self.logger.info(
                        f"Found company row with my_company_idno {my_company_idno}"
                    )
                    return row
            except Exception:
                continue

        raise Exception(f"Company row with my_company_idno {my_company_idno} not found")

    def _click_administration_button(self, row: WebElement) -> None:
        """Click administration button for a company row"""
        self.logger.info("Clicking Administration button...")
        administration_button = row.find_element(*SFSSelectors.ADMIN_BUTTON.value)
        administration_button.click()
        self.logger.info("Successfully clicked Administration button")

    def _find_and_click_efactura_block(self) -> None:
        """Find and click e-Factura block"""
        self.logger.info("Looking for e-Factura block...")
        time.sleep(2)  # Wait for blocks to load

        services_blocks = self.wait.wait_for_web_elements(
            SFSSelectors.EFACTURA_BLOCK.value
        )

        for block in services_blocks:
            if "e-Factura" in block.text:
                self.logger.info("Found e-Factura block")
                block.click()
                self.logger.info("Clicked e-Factura block")
                return

        raise Exception("e-Factura block not found")

    def _switch_to_efactura_window(self) -> None:
        """Handle window switching after clicking e-Factura block"""
        # Store the current window handle before clicking
        original_window = self.driver.current_window_handle

        time.sleep(2)  # Wait for new window

        # Wait for new window and switch to it
        WebDriverWait(self.driver, 10).until(lambda d: len(d.window_handles) > 1)

        # Switch to the new window
        for window_handle in self.driver.window_handles:
            if window_handle != original_window:
                self.driver.switch_to.window(window_handle)
                break

        # Close original window
        self.driver.switch_to.window(original_window)
        self.driver.close()

        # Switch back to e-Factura window
        self.driver.switch_to.window(self.driver.window_handles[0])
