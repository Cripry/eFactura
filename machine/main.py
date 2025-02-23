from machine.application.machine_handler import MachineHandler
from machine.config.logging_config import setup_logging


def main():
    # Setup logging
    setup_logging()

    # Create and run handler
    handler = MachineHandler(environment="TEST")
    handler.run()


if __name__ == "__main__":
    main()
