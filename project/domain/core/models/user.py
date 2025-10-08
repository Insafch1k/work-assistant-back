from project.utils.base_model import Base
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, func


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}

    user_id = Column(Integer, primary_key=True, server_default="nextval('users_user_id_seq'::regclass)")
    user_role = Column(Text, nullable=False)
    tg_username = Column(Text)
    phone = Column(Text)
    tg = Column(Text)
    rating = Column(Numeric(5, 2), nullable=False)
    user_name = Column(Text, nullable=False)
    photo = Column(Text)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    last_login_at = Column(DateTime(timezone=False), server_default=func.now())
    banned = Column(Boolean, nullable=False, server_default='false')
    is_admin = Column(Boolean, nullable=False, server_default='false')
    platform = Column(String, server_default='tg')

    def to_json(self):
        return {
            'user_id': self.user_id,
            'user_role': self.user_role,
            'tg_username': self.tg_username,
            'phone': self.phone,
            'tg': self.tg,
            'rating': float(self.rating) if self.rating else None,
            'user_name': self.user_name,
            'photo': self.photo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
            'banned': self.banned,
            'is_admin': self.is_admin,
            'platform': self.platform
        }