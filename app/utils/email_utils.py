import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime

load_dotenv()

# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = RotatingFileHandler(
    "logs/app.log",
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

class EmailConfig:
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASS = os.getenv("SMTP_PASS")
    FROM_EMAIL = os.getenv("FROM_EMAIL")

# Setup Jinja2 environment
template_dir = Path(__file__).parent.parent / "templates"
jinja_env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=True
)

def get_email_template(template_name: str, **kwargs) -> str:
    """Load and render an email template."""
    try:
        template = jinja_env.get_template(f"{template_name}.html")
        return template.render(**kwargs)
    except Exception as e:
        logger.error(f"Failed to load template {template_name}: {str(e)}")
        raise

async def send_email(to_email: str, template_name: str, subject: str, **template_data) -> bool:
    """
    Send an email using a specified template.
    
    Args:
        to_email: Recipient's email address
        template_name: Name of the template file (without .html extension)
        subject: Email subject
        **template_data: Data to be passed to the template
    """
    if not all([EmailConfig.SMTP_USER, EmailConfig.SMTP_PASS, EmailConfig.FROM_EMAIL]):
        logger.warning(
            f"SMTP not configured. Email would have been sent to {to_email}: {subject}"
        )
        return False

    try:
        # Create message
        message = MIMEMultipart()
        message["From"] = EmailConfig.FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject

        # Render template
        html_content = get_email_template(template_name, **template_data)
        message.attach(MIMEText(html_content, "html"))

        # Send email
        with smtplib.SMTP(EmailConfig.SMTP_SERVER, EmailConfig.SMTP_PORT) as server:
            server.starttls()
            server.login(EmailConfig.SMTP_USER, EmailConfig.SMTP_PASS)
            server.send_message(message)

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False