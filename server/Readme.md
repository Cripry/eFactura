# eFactura Server

## Overview

The eFactura Server is a centralized task management system that collects and distributes tasks to eFactura automation machines. It must be deployed on a server with internet access, as machines will make HTTP requests to fetch their tasks.

## System Requirements

- PostgreSQL 13+
- Python 3.10+
- Internet access
- Linux/Windows Server

## Installation

1. Clone the repository:

```bash
git clone <repository_url>
cd server
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux
# or
.\venv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create .env file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=eFactura
DB_USER=postgres
DB_PASSWORD=your_password
SECRET_KEY=your_secret_key
TOKEN_EXPIRATION=3600
```

5. Create database:

```bash
# PostgreSQL
createdb eFactura
```

6. Apply migrations:

```bash
alembic upgrade head
```

7. Start the server:

```bash
uvicorn main:app --host 0.0.0.0 --port 7989
```

## Company Registration

Before machines can fetch tasks, you need to register your company.

### Register Company Endpoint

```
POST /api/v1/companies/register
```

Request body:

```json
{
    "name": "Your Company Name"
}
```

Response:

```json
{
    "company_uuid": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Your Company Name",
    "auth_token": "46c66288ee0f092b2a25ec616cc56882cd98b57f6ab389fe5fefb871571ed11c",
    "created_at": "2024-02-14T12:00:00"
}
```

### Important: Machine Configuration

After registering your company, copy the `auth_token` from the response and add it to your machine's .env file:

```env
# machine/.env
SERVER_URL=http://your_server:7989
AUTH_TOKEN=46c66288ee0f092b2a25ec616cc56882cd98b57f6ab389fe5fefb871571ed11c
POLL_INTERVAL=10
TASK_TIMEOUT=300

# Company USB PINs
YOUR_COMPANY_NAME_SRL=123456
```

## Security Notes

- Keep your auth_token secure
- Use HTTPS in production
- Change default database credentials
- Use a strong SECRET_KEY

## Database Schema Updates

If you need to update the database schema:

1. Create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

2. Apply the migration:

```bash
alembic upgrade head
```

## Troubleshooting

- Ensure PostgreSQL is running
- Check database credentials in .env
- Verify server is accessible from machine's network
- Check logs in /var/log/eFactura/ (Linux) or Event Viewer (Windows)

## Posting Tasks

The server accepts two types of tasks: SingleInvoiceTask and MultipleInvoicesTask.

### Task Types and Actions

1. Single Invoice Tasks:
   - Used for signing individual invoices as a buyer
   - Tasks are grouped by company IDNO
   - Action type: "BuyerSignInvoice"

2. Multiple Invoice Tasks:
   - Used for bulk operations as a supplier
   - Each task represents one operation for one company
   - Action type: "SupplierSignAllDraftedInvoices"

### Endpoints

#### Post Single Invoice Tasks
```
POST /api/v1/tasks/single-invoice
```

Request body:
```json
{
    "tasks": [
        {
            "my_company_idno": "1002600012345",
            "seria": "AAB12C",
            "number": "1234567",
            "action_type": "BuyerSignInvoice"
        },
        {
            "my_company_idno": "1002600012345",
            "seria": "AAB12C",
            "number": "1234568",
            "action_type": "BuyerSignInvoice"
        }
    ]
}
```

Response:
```json
{
    "tasks": [
        {
            "task_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "status": "WAITING"
        },
        {
            "task_uuid": "660e8400-e29b-41d4-a716-446655440000",
            "status": "WAITING"
        }
    ]
}
```

#### Post Multiple Invoice Tasks
```
POST /api/v1/tasks/multiple-invoices
```

Request body:
```json
{
    "tasks": [
        {
            "my_company_idno": "1002600012345",
            "action_type": "SupplierSignAllDraftedInvoices"
        }
    ]
}
```

Response:
```json
{
    "tasks": [
        {
            "task_uuid": "770e8400-e29b-41d4-a716-446655440000",
            "status": "WAITING"
        }
    ]
}
```

Also, let me update the company registration endpoint:

```
POST /api/v1/companies/register
```

And add the task status update endpoint that machines use:

```
POST /api/v1/tasks/status
```

Request body:
```json
{
    "tasks": [
        {
            "task_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "status": "COMPLETED"
        }
    ]
}
```

### Action Types

1. SingleInvoiceAction:
   - BuyerSignInvoice: Signs an invoice as a buyer/receiver
   - (More actions can be added in future versions)

2. MultipleInvoicesAction:
   - SupplierSignAllDraftedInvoices: Signs all drafted invoices as a supplier
   - (More actions can be added in future versions)

### Task Statuses

Tasks can have the following statuses:
- WAITING: Task is queued for processing
- PROCESSING: Task is currently being executed
- COMPLETED: Task was successfully completed
- FAILED: Task execution failed
- USB_NOT_FOUND: USB certificate was not found during execution

### Important Notes

1. Authentication:
   ```
   Header: Authorization: Bearer your_auth_token
   ```

2. Rate Limits:
   - Maximum 100 tasks per request
   - Maximum 1000 requests per hour

3. Task Grouping:
   - Single invoice tasks for the same IDNO will be grouped and executed together
   - Multiple invoice tasks are executed one at a time

4. Task Lifecycle:
   - Tasks start in WAITING status
   - Machines pick up WAITING tasks
   - Final status will be COMPLETED, FAILED, or USB_NOT_FOUND
   - Tasks cannot be modified once created
