import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
import logging
from machine.invoice_signer_ddd.application.login_service import LoginService
from machine.invoice_signer_ddd.domain.models.worker import Worker
from machine.invoice_signer_ddd.infrastructure.selenium.web_driver_manager import (
    WebDriverManager,
)
from machine.invoice_signer_ddd.infrastructure.selenium.login_handler import (
    SeleniumLoginHandler,
)
from machine.invoice_signer_ddd.infrastructure.desktop.msign_handler import (
    MSignDesktopHandler,
)
from machine.invoice_signer_ddd.domain.exceptions import LoginFailedException
from machine.invoice_signer_ddd.config.logging_config import setup_logging
from machine.invoice_signer_ddd.domain.services.navigation_service import (
    NavigationService,
)


def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Initializing components...")
    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver()

    # Pass environment to handlers
    environment = "PROD"  # or "test" based on configuration
    web_handler = SeleniumLoginHandler(driver, environment)
    desktop_handler = MSignDesktopHandler()

    # Initialize NavigationService
    navigation_service = NavigationService(web_handler)

    # Pass all required dependencies to LoginService
    login_service = LoginService(
        web_handler=web_handler,
        desktop_handler=desktop_handler,
        navigation_service=navigation_service,
    )

    logger.info("Creating test worker...")
    worker = Worker(idno="1024600012882", pin="11111111")

    try:
        logger.info("Starting login process...")
        session = login_service.login_worker(worker)
        logger.info(f"Successfully logged in as worker with IDNO: {session.idno}")

    except LoginFailedException as e:
        logger.error(f"Login failed: {str(e)}")
    except Exception as e:
        logger.exception(f"Unexpected error occurred during login: {e}")
    finally:
        logger.info("Cleaning up resources...")
        driver_manager.close_driver(driver)
        logger.info("Process completed")


if __name__ == "__main__":
    main()
