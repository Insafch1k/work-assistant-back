from project.utils.base_model import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime,  func, BigInteger


class UserModel(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'public'}

    id = Column(BigInteger, primary_key=True, server_default="nextval('users_id_seq'::regclass)")
    user_role = Column(String)
    tg_username = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    tg_id = Column(Integer, nullable=True)
    user_name = Column(String)
    photo = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login_at = Column(DateTime, server_default=func.now())
    banned = Column(Boolean, server_default='false')
    is_admin = Column(Boolean, server_default='false')
    organization_name = Column(String)

