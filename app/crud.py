from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_password_hash
import uuid


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        userId=str(uuid.uuid4()),
        firstName=user.firstName,
        lastName=user.lastName,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        phone=user.phone,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_organisation(db: Session, organisation: schemas.OrganisationCreate, userId: str):
    db_org = models.Organisation(
        orgId=str(uuid.uuid4()),
        name=organisation.name,
        description=organisation.description,
        creator_id=userId
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def create_user_orgs(db: Session, data: schemas.UserOrgsCreate):
    db_org = models.User_organisation(
        id=str(uuid.uuid4()),
        userId=data.userId,
        orgId=data.orgId,
    )
    db.add(db_org)
    db.commit()
    db.refresh(db_org)
    return db_org

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()
