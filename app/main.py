from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .database import engine, Base, AsyncSessionLocal
from .routes import subscriptions
from .models import Subscription, SubscriptionStatus
from .utils.email_utils import send_email

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

app = FastAPI(
    title="Subscription Manager API",
    description="A FastAPI-based subscription management system",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(subscriptions.router)

# Initialize scheduler
scheduler = AsyncIOScheduler()

async def check_subscriptions():
    """
    Background task to check subscription status and send notifications:
    - Checks for expired subscriptions and updates their status
    - Sends notifications for expired subscriptions
    - Sends notifications for subscriptions expiring within 3 days
    """
    logger.info("Starting subscription check job")
    async with AsyncSessionLocal() as session:
        try:
            # Check for expired subscriptions
            expired_query = select(Subscription).where(
                Subscription.end_date <= datetime.utcnow(),
                Subscription.status == SubscriptionStatus.ACTIVE
            )
            result = await session.execute(expired_query)
            expired_subs = result.scalars().all()

            # Update expired subscriptions and send notifications
            for sub in expired_subs:
                logger.info(f"Processing expired subscription: {sub.id}")
                sub.status = SubscriptionStatus.EXPIRED
                
                # Send post-expiry notification
                await send_email(
                    to_email=sub.user_email,
                    template_name="post_expiry",
                    subject="Your Subscription Has Expired",
                    user_email=sub.user_email,
                    end_date=sub.end_date.strftime("%Y-%m-%d"),
                    renewal_link=f"https://your-domain.com/renew/{sub.id}"
                )

            # Check for subscriptions expiring soon (within 3 days)
            expiring_soon_query = select(Subscription).where(
                Subscription.end_date <= datetime.utcnow() + timedelta(days=3),
                Subscription.end_date > datetime.utcnow(),
                Subscription.status == SubscriptionStatus.ACTIVE
            )
            result = await session.execute(expiring_soon_query)
            expiring_soon_subs = result.scalars().all()

            # Send notifications for subscriptions expiring soon
            for sub in expiring_soon_subs:
                logger.info(f"Processing expiring soon subscription: {sub.id}")
                days_remaining = (sub.end_date - datetime.utcnow()).days
                
                # Send pre-expiry notification
                await send_email(
                    to_email=sub.user_email,
                    template_name="pre_expiry",
                    subject=f"Your Subscription Expires in {days_remaining} Days",
                    user_email=sub.user_email,
                    days_remaining=days_remaining,
                    end_date=sub.end_date.strftime("%Y-%m-%d"),
                    renewal_link=f"https://your-domain.com/renew/{sub.id}"
                )

            await session.commit()
            logger.info("Subscription check job completed successfully")

        except Exception as e:
            logger.error(f"Error in subscription check job: {str(e)}")
            raise

@app.on_event("startup")
async def startup_event():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Schedule subscription check job
    scheduler.add_job(
        check_subscriptions,
        CronTrigger(hour=0),  # Run at midnight every day
        id="check_subscriptions",
        name="Check subscription status and send notifications",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduled background tasks started")

@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()
    logger.info("Scheduled background tasks stopped")