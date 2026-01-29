from __future__ import annotations
from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, ConfigDict



class User(BaseModel):
    id: Optional[int] = None
    user_role: str
    tg_id: Optional[int] = None
    tg_username: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    auth_method: Optional[str] = None
    phone: Optional[str] = None
    user_name: str
    photo: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    banned: bool = False
    is_admin: bool = False

    model_config = ConfigDict(from_attributes=True)

    def to_json(self) -> Dict[str, Any]:
        if self.auth_method == 'telegram':
            platform_data = {
                'tg_id': self.tg_id,
                'tg_username': self.tg_username,
            }
        elif self.auth_method == 'email':
            platform_data = {
                'email': self.email,
            }
        else:
            platform_data = {}

        return {
            'id': self.id,
            'user_role': self.user_role,
            'platform_data': platform_data,
            'phone': self.phone,
            'user_name': self.user_name,
            'photo': self.photo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'banned': self.banned,
            'is_admin': self.is_admin,
        }

class UserBaseInfo(BaseModel):
    id: Optional[int] = None
    user_name: str
    photo: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


