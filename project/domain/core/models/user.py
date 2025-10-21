from project.utils.base_model import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, BigInteger, CheckConstraint

class UserModel(Base):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint(
            "auth_method = ANY (ARRAY['email'::text, 'telegram'::text])",
            name='valid_auth_method'
        ),
        {'schema': 'public'}
    )

    id = Column(Integer, primary_key=True, server_default="nextval('users_id_seq'::regclass)")
    user_role = Column(String, nullable=False)
    tg_username = Column(String)
    phone = Column(String)
    tg_id = Column(BigInteger)
    user_name = Column(String, nullable=False)
    photo = Column(String)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    last_login_at = Column(DateTime, nullable=False, server_default=func.now())
    banned = Column(Boolean, nullable=False, server_default='false')
    is_admin = Column(Boolean, nullable=False, server_default='false')
    email = Column(String)
    password_hash = Column(String)
    auth_method = Column(String, nullable=False)
