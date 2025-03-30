from sqlalchemy import create_engine, Column, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Create engine
engine = create_engine('sqlite:///data/snapp_users.db')
Base = declarative_base()

class SnappUser(Base):
    __tablename__ = 'snapp_users'
    
    phone_number = Column(String, primary_key=True)
    full_name = Column(String, nullable=True)
    access_token = Column(String)
    refresh_token = Column(String)
    login_time = Column(DateTime)
    token_expire_time = Column(DateTime)
    status = Column(Boolean, default=True)

# Create tables
Base.metadata.create_all(engine)

# Create Session class
Session = sessionmaker(bind=engine) 