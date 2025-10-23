from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional
from .models import SubscriptionStatus

class SubscriptionBase(BaseModel):
    user_email: EmailStr
    start_date: datetime
    end_date: datetime

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    end_date: datetime

class SubscriptionResponse(SubscriptionBase):
    id: int
    status: SubscriptionStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True