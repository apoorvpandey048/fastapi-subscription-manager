from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAEnum, func
from sqlalchemy.sql import expression
from datetime import datetime
import enum
from .database import Base

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True, nullable=False)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=False)
    status = Column(SQLAEnum(SubscriptionStatus), 
                   nullable=False, 
                   default=SubscriptionStatus.ACTIVE)
    created_at = Column(DateTime, 
                       nullable=False, 
                       server_default=func.now())
    updated_at = Column(DateTime, 
                       nullable=False, 
                       server_default=func.now(), 
                       onupdate=func.now())

    def __repr__(self):
        return f"<Subscription(id={self.id}, email={self.user_email}, status={self.status})>"