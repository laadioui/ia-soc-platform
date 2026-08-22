import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RoleBase(BaseModel):
    name: str
    description: str | None = None
    level: int = 0


class RoleCreate(RoleBase):
    permission_ids: list[uuid.UUID] = []


class RoleResponse(RoleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str | None = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role_ids: list[uuid.UUID] = []


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    mfa_enabled: bool
    last_login: datetime | None = None
    roles: list[RoleResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
