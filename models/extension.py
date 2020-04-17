from typing import List

from sqlalchemy import Column, String, Boolean, Text

from db import db_session
from models.base import Base


class Extension(Base):
    __tablename__ = 'extensions'

    name = Column(String, primary_key=True)
    isLoaded = Column(Boolean, server_default=u'false')
    description = Column(Text)
    author = Column(String, nullable=True)

    def __init__(self, name, is_loaded: bool):
        self.name = name
        self.isLoaded = is_loaded

    @classmethod
    def get(cls, name: str) -> 'Extension':
        return db_session.query(Extension).filter(Extension.name == name).first()

    @classmethod
    def loaded(cls) -> List['Extension']:
        return db_session.query(Extension).filter(Extension.isLoaded == 1).all()

    @classmethod
    def unloaded(cls) -> List['Extension']:
        return db_session.query(Extension).filter(Extension.isLoaded == 0).all()
