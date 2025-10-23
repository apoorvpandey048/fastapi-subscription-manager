# FastAPI Subscription Manager

A production-grade subscription management system built with FastAPI, featuring automated expiry tracking, email notifications, and background job scheduling.

## 🚀 Features

- **RESTful API Endpoints**: Create, read, update, renew, and delete subscriptions
- **Automated Expiry System**: Background jobs check subscription status every 24 hours
- **Email Notifications**: HTML email templates for pre-expiry and post-expiry alerts
- **Database Support**: SQLite (default) and PostgreSQL compatibility with async support
- **Production Logging**: Rotating file handler with 10MB rotation and 5 backup files
- **CORS Enabled**: Ready for frontend integration
- **Type Safety**: Pydantic schemas for request/response validation

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Automated Email Alerts and Background Jobs](#automated-email-alerts-and-background-jobs)
- [Database Models](#database-models)
- [Logging](#logging)
- [Development](#development)
- [Production Deployment](#production-deployment)

## 🛠 Tech Stack

- **Framework**: FastAPI 0.68.0+
- **Database**: SQLAlchemy (async) with SQLite/PostgreSQL
- **Task Scheduler**: APScheduler 3.8.1+
- **Email Templates**: Jinja2 3.0.0+
- **ASGI Server**: Uvicorn 0.15.0+
- **Python**: 3.8+

## 📁 Project Structure

```
fastapi-subscription-manager/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app, startup/shutdown events, scheduler
│   ├── database.py             # Database engine, session management
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas for validation
│   ├── routes/
│   │   ├── __init__.py
│   │   └── subscriptions.py   # Subscription CRUD endpoints
│   ├── templates/
│   │   ├── pre_expiry.html    # Email template for expiring subscriptions
│   │   └── post_expiry.html   # Email template for expired subscriptions
│   └── utils/
│       ├── __init__.py
│       └── email_utils.py     # Email sending utilities with Jinja2
├── logs/
│   └── app.log                # Application logs (auto-created)
├── .env                       # Environment variables (create from .env.example)
├── .env.example               # Environment variables template
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- (Optional) PostgreSQL database

### Step 1: Clone the Repository

```powershell
git clone https://github.com/apoorvpandey048/fastapi-subscription-manager.git
cd fastapi-subscription-manager
```

### Step 2: Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```powershell
cp .env.example .env
```

Edit `.env` with your configuration (see [Configuration](#configuration) section).

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```bash
# Database Configuration
DB_TYPE=sqlite                    # or 'postgresql'
DB_USER=your_db_user              # Required for PostgreSQL
DB_PASSWORD=your_db_password      # Required for PostgreSQL
DB_HOST=localhost                 # Required for PostgreSQL
DB_NAME=subscriptions             # Database name

# Email Configuration (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=youremail@gmail.com
SMTP_PASS=yourpassword            # For Gmail, use App Password
FROM_EMAIL=Subscription Manager <youremail@gmail.com>

# Application Settings
LOG_LEVEL=INFO
RENEWAL_BASE_URL=https://your-domain.com/renew
```

### Gmail SMTP Setup

For Gmail, you need to:
1. Enable 2-Factor Authentication
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Use the App Password in `SMTP_PASS`

### PostgreSQL Setup

If using PostgreSQL instead of SQLite:

```bash
DB_TYPE=postgresql
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_NAME=subscriptions
```

## 🏃 Running the Application

### Development Mode

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: `http://localhost:8000`
- Interactive Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔌 API Endpoints

### Base URL: `/subscriptions`

| Method | Endpoint | Description | Request Body |
|--------|----------|-------------|--------------|
| POST | `/subscriptions/` | Create a new subscription | `SubscriptionCreate` |
| GET | `/subscriptions/{id}` | Get subscription by ID | - |
| PUT | `/subscriptions/{id}/renew` | Renew a subscription | `SubscriptionUpdate` |
| DELETE | `/subscriptions/{id}` | Delete a subscription | - |

### Request/Response Examples

#### Create Subscription

```bash
POST /subscriptions/
Content-Type: application/json

{
  "user_email": "user@example.com",
  "start_date": "2025-10-23T00:00:00",
  "end_date": "2025-11-23T00:00:00"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "user_email": "user@example.com",
  "start_date": "2025-10-23T00:00:00",
  "end_date": "2025-11-23T00:00:00",
  "status": "active",
  "created_at": "2025-10-23T10:30:00",
  "updated_at": "2025-10-23T10:30:00"
}
```

#### Get Subscription

```bash
GET /subscriptions/1
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_email": "user@example.com",
  "start_date": "2025-10-23T00:00:00",
  "end_date": "2025-11-23T00:00:00",
  "status": "active",
  "created_at": "2025-10-23T10:30:00",
  "updated_at": "2025-10-23T10:30:00"
}
```

#### Renew Subscription

```bash
PUT /subscriptions/1/renew
Content-Type: application/json

{
  "end_date": "2025-12-23T00:00:00"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_email": "user@example.com",
  "start_date": "2025-10-23T00:00:00",
  "end_date": "2025-12-23T00:00:00",
  "status": "active",
  "created_at": "2025-10-23T10:30:00",
  "updated_at": "2025-10-23T11:00:00"
}
```

#### Delete Subscription

```bash
DELETE /subscriptions/1
```

**Response (204 No Content)**

## 📧 Automated Email Alerts and Background Jobs

### Background Job System

The application includes an automated background job powered by **APScheduler** that runs every 24 hours at midnight (00:00) to:

#### 1. **Expired Subscriptions**
- Queries all subscriptions where `end_date <= current_date` and `status = 'active'`
- Updates subscription status to `"expired"`
- Sends post-expiry notification email using `post_expiry.html` template
- Logs all status changes and email attempts

#### 2. **Soon-to-Expire Subscriptions**
- Queries subscriptions where `end_date` is within the next 3 days
- Sends pre-expiry notification email using `pre_expiry.html` template
- Includes days remaining in the email
- Does not change subscription status

#### Job Configuration

Located in `app/main.py`:
```python
scheduler.add_job(
    check_subscriptions,
    CronTrigger(hour=0),  # Run at midnight every day
    id="check_subscriptions",
    name="Check subscription status and send notifications",
    replace_existing=True
)
```

### Email Template System

The application uses **Jinja2** templates for sending professional HTML emails with inline CSS.

#### Templates

1. **`pre_expiry.html`**: Sent 3 days before subscription expiration
   - Blue header color (#4a90e2)
   - Displays days remaining
   - Includes renewal link button

2. **`post_expiry.html`**: Sent when a subscription expires
   - Red header color (#e74c3c)
   - Notifies of expired status
   - Includes reactivation link button

#### Email Sending Function

Located in `app/utils/email_utils.py`:
```python
await send_email(
    to_email="user@example.com",
    template_name="pre_expiry",
    subject="Your Subscription Expires in 3 Days",
    user_email="user@example.com",
    days_remaining=3,
    end_date="2025-10-26",
    renewal_link="https://your-domain.com/renew/123"
)
```

#### Example Email Alert Payload

```json
{
    "template": "pre_expiry",
    "recipient": "user@example.com",
    "data": {
        "user_email": "user@example.com",
        "days_remaining": 3,
        "end_date": "2025-10-26",
        "renewal_link": "https://your-domain.com/renew/123"
    }
}
```

### Manual Testing

To manually test the background job without waiting 24 hours:

```python
# Add this to test the scheduler immediately
import asyncio
from app.main import check_subscriptions

# Run the job manually
asyncio.run(check_subscriptions())
```

## 🗄️ Database Models

### Subscription Model

Located in `app/models.py`:

```python
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id: int                          # Primary key
    user_email: str                  # User's email address
    start_date: datetime             # Subscription start date
    end_date: datetime               # Subscription end date
    status: SubscriptionStatus       # 'active' or 'expired'
    created_at: datetime             # Record creation timestamp
    updated_at: datetime             # Record update timestamp
```

### Subscription Status Enum

```python
class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
```

## 📊 Logging

### Configuration

- **Handler**: RotatingFileHandler
- **Log File**: `logs/app.log`
- **Max Size**: 10 MB per file
- **Backup Count**: 5 files
- **Log Level**: INFO
- **Format**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### Log Locations

Logging is configured in:
- `app/main.py` - Main application and scheduler logs
- `app/utils/email_utils.py` - Email sending logs

### Example Log Output

```
2025-10-23 00:00:01 - __main__ - INFO - Starting subscription check job
2025-10-23 00:00:02 - __main__ - INFO - Processing expired subscription: 123
2025-10-23 00:00:03 - email_utils - INFO - Email sent successfully to user@example.com
2025-10-23 00:00:04 - __main__ - INFO - Processing expiring soon subscription: 456
2025-10-23 00:00:05 - __main__ - INFO - Subscription check job completed successfully
```

### Viewing Logs

```powershell
# View recent logs
Get-Content logs\app.log -Tail 50

# Follow logs in real-time
Get-Content logs\app.log -Wait
```

## 🧪 Development

### Project Dependencies

Key dependencies from `requirements.txt`:

```
fastapi>=0.68.0              # Web framework
uvicorn>=0.15.0              # ASGI server
sqlalchemy>=1.4.0            # ORM
apscheduler>=3.8.1           # Background job scheduler
python-dotenv>=0.19.0        # Environment variable management
jinja2>=3.0.0                # Email templating
aiosqlite>=0.17.0            # Async SQLite driver
asyncpg>=0.24.0              # Async PostgreSQL driver
pydantic>=1.8.0              # Data validation
email-validator>=1.1.0       # Email validation
```

### Code Structure

- **Async/Await**: All database operations use async/await patterns
- **Dependency Injection**: FastAPI's dependency system for database sessions
- **Type Hints**: Full type annotations throughout
- **Pydantic Models**: Request/response validation with Pydantic schemas
- **SQLAlchemy ORM**: Async SQLAlchemy for database operations

### Adding New Features

1. **New Endpoint**: Add to `app/routes/subscriptions.py`
2. **New Model**: Update `app/models.py` and create migration
3. **New Schema**: Add to `app/schemas.py`
4. **New Background Job**: Add to `app/main.py` scheduler section

## 🚢 Production Deployment

### Using Docker (Recommended)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```powershell
docker build -t subscription-manager .
docker run -p 8000:8000 --env-file .env subscription-manager
```

### Environment Variables for Production

Ensure these are set:
- Use PostgreSQL instead of SQLite
- Set strong SMTP credentials
- Configure proper CORS origins
- Set `LOG_LEVEL=WARNING` or `ERROR`
- Use HTTPS for `RENEWAL_BASE_URL`

### Security Considerations

1. **Never commit `.env` file** - Use `.env.example` as template
2. **Use app passwords** for email SMTP (not account password)
3. **Set proper CORS origins** instead of `["*"]`
4. **Use HTTPS** in production
5. **Implement rate limiting** for API endpoints
6. **Add authentication/authorization** for sensitive operations

### Monitoring

Monitor these files/metrics:
- `logs/app.log` - Application logs
- Database connection pool
- Email sending success rate
- Background job execution times

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues or questions, please open an issue on GitHub or contact the maintainer.

---

**Built with ❤️ using FastAPI**
