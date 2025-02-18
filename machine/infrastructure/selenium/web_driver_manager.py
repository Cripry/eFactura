from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging


class WebDriverManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_driver(self):
        """Get a configured Chrome WebDriver instance"""
        self.logger.info("Initializing Chrome WebDriver")

        # Configure Chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")  # Start maximized
        # chrome_options.add_argument("--start-fullscreen")  # Start in fullscreen mode
        chrome_options.add_argument("--disable-infobars")  # Disable infobars
        # Initialize WebDriver with options
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()), options=chrome_options
            )
            self.logger.info("Chrome WebDriver initialized successfully")
            return driver
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {str(e)}")
            raise

    def close_driver(self, driver: webdriver.Chrome) -> None:
        driver.quit()
