# FastAPI Subscription Manager

[Previous content remains the same...]

## Automated Email Alerts and Background Jobs

### Background Job System

The application includes an automated background job system that runs every 24 hours at midnight to:

1. Check for expired subscriptions:
   - Updates subscription status to "expired"
   - Sends post-expiry notifications
   - Logs status changes

2. Check for soon-to-expire subscriptions:
   - Identifies subscriptions expiring within 3 days
   - Sends pre-expiry notifications
   - Logs notification attempts

### Email Template System

The application uses Jinja2 templates for sending professional HTML emails:

- `pre_expiry.html`: Sent 3 days before subscription expiration
- `post_expiry.html`: Sent when a subscription expires

Example email alert payload:

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