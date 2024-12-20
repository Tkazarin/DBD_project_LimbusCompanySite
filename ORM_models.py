from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from database import Base



class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    login = Column(String(150), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)

    reading_list = relationship("ReadingList", back_populates="user")

class Source(Base):
    __tablename__ = 'source'

    source_id = Column(Integer, primary_key=True)
    title = Column(String(150))
    author = Column(String(150))
    file = Column(String(256))

    source_char = relationship("Characters", back_populates="characters")
    source_sin = relationship("Sinners", back_populates="sinner")
    source_read_list = relationship("ReadingList", back_populates="source")

class Characters(Base):
    __tablename__ = 'characters'

    character_id = Column(Integer, primary_key=True)
    name = Column(String(150))
    file = Column(String(256))
    source_id = Column(Integer, ForeignKey("source.source_id"))
    characters = relationship("Source", back_populates="source_char")

class EGO(Base):
    __tablename__ = 'ego'

    ego_id = Column(Integer, primary_key=True)
    title = Column(String(150))
    abnormality = Column(String(150))
    file = Column(String(256))
    ego_sinner = relationship("SinnerEgo", back_populates="ego")

class Sinners(Base):
    __tablename__ = 'sinners'

    sinner_id = Column(Integer, primary_key=True)
    name = Column(String(150))
    nick = Column(String(150))
    file = Column(String(256))
    source_id = Column(Integer, ForeignKey("source.source_id"))
    sinner = relationship("Source", back_populates="source_sin")
    sinner_ide = relationship("Identity", back_populates="sinner")
    sinner_ego = relationship("SinnerEgo", back_populates="sinner")

class Identity(Base):
    __tablename__ = 'identity'

    identity_id = Column(Integer, primary_key=True)
    title = Column(String(150))
    rarity = Column(String(5))
    file = Column(String(256))
    sinner_id = Column(Integer, ForeignKey("sinners.sinner_id"))
    sinner = relationship("Sinners", back_populates="sinner_ide")

class SinnerEgo(Base):
    __tablename__ = 'sinner_ego'

    sinner_id = Column(Integer, ForeignKey('sinners.sinner_id'), primary_key=True)
    ego_id = Column(Integer, ForeignKey('ego.ego_id'), primary_key=True)
    level = Column(String(10), nullable=False)
    file = Column(String(255), nullable=True)

    ego = relationship("EGO", back_populates="ego_sinner")
    sinner = relationship("Sinners", back_populates="sinner_ego")

class ReadingList(Base):
    __tablename__ = 'reading_list'

    reading_list_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    source_id = Column(Integer, ForeignKey("source.source_id"))
    date_of_adding = Column(Date)
    status = Column(Boolean)

    user = relationship("Users", back_populates="reading_list")
    source = relationship("Source", back_populates="source_read_list")