from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime
from typing import List

from ..database import get_db
from ..models import Subscription, SubscriptionStatus
from ..schemas import SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse
from ..utils.email_utils import send_email

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionCreate,
    db: AsyncSession = Depends(get_db)
):
    db_subscription = Subscription(
        user_email=subscription.user_email,
        start_date=subscription.start_date,
        end_date=subscription.end_date,
        status=SubscriptionStatus.ACTIVE
    )
    
    db.add(db_subscription)
    await db.commit()
    await db.refresh(db_subscription)
    return db_subscription

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Subscription).filter(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    return subscription

@router.put("/{subscription_id}/renew", response_model=SubscriptionResponse)
async def renew_subscription(
    subscription_id: int,
    update_data: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Subscription).filter(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    subscription.end_date = update_data.end_date
    subscription.status = SubscriptionStatus.ACTIVE
    
    await db.commit()
    await db.refresh(subscription)
    
    return subscription

@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Subscription).filter(Subscription.id == subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )
    
    await db.delete(subscription)
    await db.commit()