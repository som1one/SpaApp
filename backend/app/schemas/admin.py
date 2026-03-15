from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.admin import AdminRole


class AdminInviteBase(BaseModel):
    email: EmailStr
    role: str = AdminRole.ADMIN.value

class AdminInviteRequest(AdminInviteBase):
    pass


class AdminInviteResponse(AdminInviteBase):
    token: str
    status: str
    expires_at: datetime
    accepted: bool
    invited_by_email: EmailStr | None = None
    created_at: datetime


class AdminAcceptInviteRequest(BaseModel):
    token: str = Field(..., min_length=32, max_length=64)
    password: str = Field(..., min_length=8, max_length=72)


class AdminAcceptInviteResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    profile: "AdminProfile"


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminProfile(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool
    is_authenticated: bool = True


class AdminInvitePublicResponse(BaseModel):
    email: EmailStr
    role: str
    status: str
    expires_at: datetime


class AdminInviteListResponse(BaseModel):
    invites: list[AdminInviteResponse]


AdminAcceptInviteResponse.model_rebuild()



