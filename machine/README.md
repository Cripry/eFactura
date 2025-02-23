# eFactura Machine

## Overview

eFactura Machine is the executor component that runs on a computer with USB certificate keys attached. It periodically checks for tasks from the eFactura Server and executes them using the appropriate USB certificates.

## System Requirements

- Windows 10+ (required for MSign Desktop)
- Python 3.10+
- Chrome Browser
- MSign Desktop Application
- USB ports for certificate keys
- Internet access

## Installation

1. Clone the repository:
```bash
git clone <repository_url>
cd machine
```

2. Create a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Install the package in development mode:
```bash
pip install -e .
```

## Configuration

1. Create .env file in the machine directory:
```env
# Server Connection
SERVER_URL=http://your_server:7989
AUTH_TOKEN=your_auth_token_from_server  # Get this from server after company registration

# Task Check Interval
POLL_INTERVAL=10  # Seconds between task checks
TASK_TIMEOUT=300  # Task execution timeout

# Company USB PINs - Add your company's USB PIN
COMPANY_NAME_SRL_PIN=123456  # Example: STARNET_SRL_PIN=123456
```

2. Update USB_PIN mapping in config/config.py:
```python
class USB_PIN:
    """Configuration for USB PINs mapped to company IDNOs"""

    # Map IDNO to environment variable names
    IDNO_MAP = {
        "1234567890123": "COMPANY_NAME_SRL_PIN",  # Example: "1002600012345": "STARNET_SRL_PIN"
    }
```

## Running the Application

1. Ensure all USB certificate keys are properly connected

2. Start the application:
```bash
python -m machine.main
```

The application will:
- Connect to the configured server
- Check for new tasks every POLL_INTERVAL seconds
- Execute tasks using the appropriate USB certificates
- Report task status back to the server

## Task Types

The machine handles two types of tasks:

1. Single Invoice Tasks:
   - Signs individual invoices
   - Requires specific invoice seria and number
   - Uses buyer role

2. Multiple Invoice Tasks:
   - Signs all drafted invoices
   - Uses supplier role
   - Processes all pending invoices at once

## Troubleshooting

- Verify USB certificates are properly connected
- Check .env configuration
- Ensure MSign Desktop is running
- Verify server connection
- Check logs in machine/logs/machine.log

## Security Notes

- Keep USB PINs secure
- Don't share .env file
- Store USB certificates safely
- Use strong PINs
- Keep auth_token confidential

## Example Configuration

Here's a complete example of the required configuration:

1. .env file:
```env
# Server Connection
SERVER_URL=http://192.168.1.100:7989
AUTH_TOKEN=46c66288ee0f092b2a25ec616cc56882cd98b57f6ab389fe5fefb871571ed11c

# Task Settings
POLL_INTERVAL=10
TASK_TIMEOUT=300

# Company USB PINs
STARNET_SRL_PIN=123456
MOLDCELL_SA_PIN=654321
```

2. config/config.py IDNO mapping:
```python
IDNO_MAP = {
    "1002600012345": "STARNET_SRL_PIN",
    "1002600054321": "MOLDCELL_SA_PIN",
}
```

## Logs

The application logs are stored in:
```
machine/logs/machine.log
```

Use these logs for debugging and monitoring task execution. 