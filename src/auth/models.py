from sqlalchemy import String, Column, Table, MetaData, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()
metadata = MetaData()

user_table = Table(
    "users",
    metadata,
    Column("id", Integer(), primary_key=True, autoincrement=True, nullable=False),
    Column("email", String(), index=True, primary_key=True),
    Column("hashed_password", String()),
    Column("account_created", String(), nullable=False)
)


class User(Base):
    __tablename__ = "users"
    id = Column("id", Integer(), primary_key=True, autoincrement=True, nullable=False)
    email = Column("email", String(length=320), index=True, nullable=False, primary_key=True)
    hashed_password = Column("hashed_password", String(length=1024), nullable=False)
    account_created = Column("account_created", String(length=100), nullable=False)
