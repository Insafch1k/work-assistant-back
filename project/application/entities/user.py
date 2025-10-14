from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    id: int
    user_role: str
    tg_username: Optional[str] = None
    phone: Optional[str] = None
    tg_id: Optional[int] = None
    user_name: Optional[str] = None
    photo: Optional[str] = None
    created_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    banned: bool = False
    is_admin: bool = False
    organization_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    def to_json(self):
        return {
            'id': self.id,
            'user_role': self.user_role,
            'tg_username': self.tg_username,
            'phone': self.phone,
            'tg_id': self.tg_id,
            'user_name': self.user_name,
            'photo': self.photo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'banned': self.banned,
            'is_admin': self.is_admin,
            'organization_name': self.organization_name
        }