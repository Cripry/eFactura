import logging
from application.machine_handler import MachineHandler


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def main():
    setup_logging()
    handler = MachineHandler()
    handler.run()


if __name__ == "__main__":
    main()
