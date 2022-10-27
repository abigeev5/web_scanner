from db_session import SqlAlchemyBase
from sqlalchemy import Column, String, Integer, DATETIME, ForeignKey, JSON, BOOLEAN
from sqlalchemy.orm import relationship


class User(SqlAlchemyBase):
	__tablename__ = 'users'
	
	id = Column(Integer, primary_key=True)
	username = Column(String)
	information = Column(String)
	FIO = Column(String)
	password = Column(String)
	token = Column(String)
	role = Column(Integer)


class Scanner(SqlAlchemyBase):
	__tablename__ = 'scanners'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)
	version = Column(Integer)
	description = Column(Integer)
	settings = Column(JSON)
	connection = Column(JSON)
	metadata_ = Column('metadata', JSON)
	operators = Column(String)
	notifications = Column(JSON)


class Result(SqlAlchemyBase):
	__tablename__ = 'results'
	
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.id'))
	scanner_id = Column(Integer, ForeignKey('scanners.id'))
	barcode = Column(Integer)
	date = Column(DATETIME)
	results = Column(JSON)
	enterobiasis = Column(BOOLEAN)
	folder_path = Column(String)