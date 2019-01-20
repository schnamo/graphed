from sqlalchemy import create_engine, MetaData, sql
from sqlalchemy import Table, Column, Integer, String, Boolean, Date, Time, Binary, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///data.db")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True)
    passhash = Column(Binary(32))

class Workspace(Base):
    __tablename__ = "workspaces"
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(Integer, ForeignKey(User.id))
    name = Column(String(64))

class Note(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace = Column(Integer, ForeignKey(Workspace.id))
    name = Column(String(64))

class Connection(Base):
    __tablename__ = "connections"
    id = Column(Integer, primary_key=True, autoincrement=True)
    workspace = Column(Integer, ForeignKey(Workspace.id))
    origin = Column(Integer, ForeignKey(Note.id))
    target = Column(Integer, ForeignKey(Note.id))

class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(ForeignKey(User.id))
    token = Column(Binary(32), unique=True)

Base.metadata.create_all(engine)
Session = sessionmaker()
Session.configure(bind=engine)
