from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from machine.invoice_signer_ddd.domain.models.worker import Worker
from machine.invoice_signer_ddd.domain.models.session import Session
from machine.invoice_signer_ddd.infrastructure.selenium.selectors import (
    LoginPageSelectors,
)
from machine.invoice_signer_ddd.domain.exceptions import CertificateNotFoundException
from machine.invoice_signer_ddd.infrastructure.config.environment_config import (
    EnvironmentConfig,
)
from machine.invoice_signer_ddd.infrastructure.selenium.wait_helper import (
    WaitHelper,
)
from machine.invoice_signer_ddd.domain.models.component_characteristics import (
    ComponentCharacteristics,
)
from machine.invoice_signer_ddd.infrastructure.selenium.wait_condition_handler import (
    WaitConditionHandler,
)
import logging
import time
from selenium.webdriver.support.select import Select


class SeleniumLoginHandler:
    def __init__(self, driver: WebDriver, environment: str):
        self.driver = driver
        self.environment = environment
        self.base_url = EnvironmentConfig.get_base_url(environment)
        self.wait = WaitHelper(self.driver, 10)
        self.condition_handler = WaitConditionHandler(self.driver)
        self.logger = logging.getLogger(__name__)

    def navigate_to_sfs(self) -> None:
        self.logger.info(f"Navigating to SFS portal: {self.base_url}")
        self.driver.get(self.base_url)

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

    def select_certificate(self, idno: str) -> bool:
        self.logger.info(f"Selecting certificate for IDNO: {idno}")

        try:
            # Wait for certificate page to load
            self.condition_handler.wait_for_characteristics(
                ComponentCharacteristics.CERTIFICATE_PAGE
            )

            container = self.driver.find_element(
                *LoginPageSelectors.CERTIFICATES_CONTAINER.value
            )
            certificates = container.find_elements(By.TAG_NAME, "button")

            for cert in certificates:
                if idno in cert.text:
                    self.logger.debug(f"Found matching certificate: {cert.text}")
                    cert.click()
                    return True

            raise CertificateNotFoundException(idno)
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
            self.select_certificate(worker.idno)

            self.logger.info("Web authentication and certificate selection completed")
            return Session(idno=worker.idno)
        except Exception as e:
            self.logger.error(f"Web authentication failed: {str(e)}")
            raise Exception(f"Web authentication failed: {str(e)}")

    def select_company_and_role(self, worker: Worker) -> None:
        """Select company and role after successful authentication"""
        self.logger.info("Starting company and role selection")
        try:
            # 1. Select juridic person type
            self.logger.debug("Selecting person type...")
            person_type_select = self.wait.wait_for_web_element(
                LoginPageSelectors.PERSON_TYPE_SELECT.value
            )
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

            # Find company by IDNO
            companies_container = self.wait.wait_for_web_element(
                LoginPageSelectors.COMPANIES_LIST.value
            )
            companies = companies_container.find_elements(
                *LoginPageSelectors.COMPANY_ITEMS.value
            )

            company_found = False
            for company in companies:
                if worker.idno in company.text:
                    self.logger.info(f"Found company with IDNO {worker.idno}")
                    company.click()
                    company_found = True
                    break

            if not company_found:
                raise Exception(f"Company with IDNO {worker.idno} not found")

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
