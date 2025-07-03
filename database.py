from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#mysql creds 
#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:password@localhost:3306/bitespeed"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:hrishi2002@localhost:3306/bitespeed"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
 