from sqlalchemy import Column, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.db import Base




class User_organisation(Base):
    __tablename__ = "users_organisation"
    id = Column(String, primary_key=True, index=True, unique=True)
    userId = Column(String , ForeignKey('users.userId'))
    orgId = Column(String, ForeignKey('organisations.orgId'))

class User(Base):
    __tablename__ = "users"

    userId = Column(String, primary_key=True, index=True, unique=True)
    firstName = Column(String, nullable=False)
    lastName = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    phone = Column(String)
    
    #organisations = relationship("Organisation", secondary="user_organisation", back_populates="users")
    # organisations = relationship(
    #     "Organisation",
    #     secondary=user_organisation,
    #     back_populates="users"
    # )


class Organisation(Base):
    __tablename__ = "organisations"

    orgId = Column(String, primary_key=True, index=True, unique=True)
    name = Column(String, nullable=False)
    description = Column(String)
    creator_id = Column(String, ForeignKey('users.userId'))

    #users = relationship("User", secondary="user_organisation", back_populates="organisations")
    # users = relationship(
    #     "User",
    #     secondary=user_organisation,
    #     back_populates="organisations"
    # )


