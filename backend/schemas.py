from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class ContactBase(BaseModel):
    name: str
    company: Optional[str] = None
    email: EmailStr
    message: str

class ContactCreate(ContactBase):
    pass

class ContactResponse(ContactBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
