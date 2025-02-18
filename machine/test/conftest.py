import pytest
from selenium.webdriver import Chrome
from machine.infrastructure.selenium.core.web_driver_facade import (
    WebDriverFacade,
)


@pytest.fixture
def web_driver():
    driver = Chrome()
    yield WebDriverFacade(driver)
    driver.quit()
