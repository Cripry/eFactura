from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, parse_qs
from machine.invoice_signer_ddd.domain.models.urls import UrlPaths, QueryParams
from typing import Tuple
from selenium.webdriver.remote.webelement import WebElement


class WaitHelper:
    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.timeout = timeout

    def wait_for_web_element(self, selector: Tuple[By, str]):
        """Wait for a web element to be present"""
        return self.wait.until(EC.presence_of_element_located(selector))

    def wait_for_web_element_clickable(
        self, selector: Tuple[By, str], timeout: int = None
    ) -> WebElement:
        """
        Wait for a web element to be clickable with optional custom timeout

        Args:
            selector: Tuple containing By and selector value
            timeout: Optional custom timeout in seconds (default: instance timeout)

        Returns:
            WebElement: The clickable web element

        Raises:
            TimeoutException: If element not found within timeout
        """
        # Use custom timeout if provided, otherwise use instance timeout
        wait_timeout = timeout if timeout is not None else self.timeout
        wait = WebDriverWait(self.driver, wait_timeout)

        return wait.until(EC.element_to_be_clickable(selector))

    def wait_for_web_elements(self, selector: Tuple[By, str]):
        """Wait for multiple web elements to be present"""
        return self.wait.until(EC.presence_of_all_elements_located(selector))

    def wait_for_url_path(self, path: UrlPaths) -> bool:
        """Wait until current URL contains specified path"""
        return self.wait.until(
            lambda driver: path.value in urlparse(driver.current_url).path
        )

    def wait_for_query_param(self, param: QueryParams, value: str = None) -> bool:
        """Wait until current URL contains specified query parameter"""

        def param_condition(driver):
            query = urlparse(driver.current_url).query
            params = parse_qs(query)
            if param.value in params:
                if value is None:
                    return True
                return value in params[param.value]
            return False

        return self.wait.until(param_condition)

    def wait_for_condition(self, condition) -> bool:
        """Wait for custom condition"""
        return self.wait.until(condition)

    def wait_for_url_and_params(
        self,
        path: UrlPaths = None,
        query_param: QueryParams = None,
        param_value: str = None,
        timeout: int = 10,
    ) -> bool:
        """Wait until both URL path and query parameter match"""

        def combined_condition(driver):
            url = urlparse(driver.current_url)

            # Check path if provided
            if path is not None and path.value not in url.path:
                return False

            # Check query parameter if provided
            if query_param is not None:
                params = parse_qs(url.query)
                if query_param.value not in params:
                    return False
                if (
                    param_value is not None
                    and param_value not in params[query_param.value]
                ):
                    return False

            return True

        # Create temporary wait with custom timeout
        temp_wait = WebDriverWait(self.driver, timeout, poll_frequency=2)
        return temp_wait.until(combined_condition)
