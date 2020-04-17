from datetime import datetime

from sqlalchemy import Column, String, DateTime

from db import db_session
from models.base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    discord_id = Column(String, unique=True, nullable=False)
    mail_address = Column(String, unique=True, nullable=False)
    verified_at = Column(DateTime, default=None)

    @classmethod
    def get(cls, user_id: str = None, discord_id: str = None, mail_address: str = None,
            verified_at: datetime = None) -> 'User':
        f = [col == val for (col, val) in (
            (User.id, user_id),
            (User.discord_id, discord_id),
            (User.mail_address, mail_address),
            (User.verified_at, verified_at),
        ) if val is not None]
        return db_session.query(User).filter(*f).first()

    @classmethod
    def exists(cls, user_id: str = None, discord_id: str = None, mail_address: str = None,
               verified_at: datetime = None) -> bool:
        return User.get(user_id, discord_id, mail_address, verified_at) is not None
