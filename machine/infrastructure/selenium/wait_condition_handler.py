from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from machine.domain.models.selectors.component_characteristics import (
    ComponentCharacteristics,
)


class WaitConditionHandler:
    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.driver = driver
        self.timeout = timeout

    def wait_for_characteristics(
        self, characteristics: ComponentCharacteristics
    ) -> bool:
        selector, conditions = characteristics.value
        wait = WebDriverWait(self.driver, self.timeout)

        try:
            wait.until(EC.presence_of_element_located(selector))

            if "text" in conditions:
                wait.until(
                    EC.text_to_be_present_in_element(selector, conditions["text"])
                )

            return True
        except Exception as e:
            raise Exception(f"Failed to meet characteristics: {str(e)}")

    def wait_until_url_matches_domain(self, base_url: str) -> bool:
        """
        Wait until the current URL matches the provided base URL.

        Args:
            base_url: The base URL to match against (domain name)

        Returns:
            bool: True if the condition is met within the timeout

        Raises:
            Exception: If the URL doesn't match within the timeout
        """
        wait = WebDriverWait(self.driver, 60)

        try:
            wait.until(lambda driver: driver.current_url.startswith(base_url))
            return True
        except Exception as e:
            raise Exception(f"URL did not match {base_url} within timeout: {str(e)}")
