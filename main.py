from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from app import models, schemas, crud
from app.db import SessionLocal, engine
from app.auth import create_access_token, verify_password
from datetime import timedelta
from app.config import settings
from app.exceptions import http_exception_handler, NotFoundError, AuthError, RegistrationError
import secrets


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_exception_handler(HTTPException, http_exception_handler)

# Declaration of the HTTP Basic Authentication method
security = HTTPBearer()

# Declaration of the Bearer schema for token-based authentication

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
security = HTTPBearer()

def get_current_user(request: Request, db: Session = Depends(get_db)):
    auth_header: Optional[str] = request.headers.get('Authorization')
    if auth_header is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = auth_header.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        userId: str = payload.get("sub")
        if userId is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(models.User).filter(models.User.userId == userId).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


@app.post("/auth/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise RegistrationError(
            detail="Registration unsuccessful",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_user = crud.create_user(db=db, user=user)
    default_org = schemas.OrganisationCreate(name=f"{db_user.firstName}'s Organisation", description="Default organisation")
    db_orgs = crud.create_organisation(db=db, organisation=default_org, userId=db_user.userId)
    db_user_org = schemas.UserOrgsCreate(userId=db_user.userId, orgId=db_orgs.orgId)
    crud.create_user_orgs(db=db, data=db_user_org)
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.userId}, expires_delta=access_token_expires
    )
    content ={ 
            "status": "success",  
            "message": "Registration successful",  
            "data": {
                "accessToken": access_token, 
                "user": {
                    "userId": db_user.userId,
                    "firstName": db_user.firstName,
                    "lastName": db_user.lastName,
                    "email": db_user.email,
                    "phone": db_user.phone,
                }
            }
        }
    return JSONResponse(content, status_code=status.HTTP_201_CREATED)

@app.post("/auth/login")
def login_for_access_token(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise AuthError(
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.userId}, expires_delta=access_token_expires
    )
    return JSONResponse({ 
            "status": "success",  
            "message": "Login successful",  
            "data": {
                "accessToken": access_token, 
                "user": {
                    "userId": user.userId,
                    "firstName": user.firstName,
                    "lastName": user.lastName,
                    "email": user.email,
                    "phone": user.phone,
                }
            }
        }
    )
    
@app.get("/api/users/{userId}")
def get_user(userId: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.userId == userId).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    content = {
		"status": "success",
        "message": "User data fetched successful",
        "data": {
            "userId": user.userId,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "email":  user.email,
            "phone":  user.phone,
        }
    }
    return JSONResponse(content, status_code=status.HTTP_200_OK)

@app.get("/api/organisations")
def get_user(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    organisations = db.query(models.User_organisation).filter(models.User_organisation.userId == current_user.userId).all()
    orgData = []
    for org in organisations:
        orgs = db.query(models.Organisation).filter(models.Organisation.orgId == org.orgId).first()
        orgData.append({
            'orgId': orgs.orgId,
            'name': orgs.name,
            'description': orgs.description
        })
    print(orgData)
    return {
        "status": "success",
        "message": "Organisations retrieved successfully",
        "data": {"organisations": orgData}
    }

@app.post("/api/organisations", status_code=status.HTTP_201_CREATED)
def create_organisation(organisation: schemas.OrganisationCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_data = db.query(models.Organisation).filter(models.Organisation.name == organisation.name).first()
    if db_data is not None:
        raise RegistrationError(
            detail="Client error",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_org = crud.create_organisation(db=db, organisation=organisation, userId=current_user.userId)
    db_user_org = schemas.UserOrgsCreate(userId=db_org.creator_id, orgId=db_org.orgId)
    crud.create_user_orgs(db=db, data=db_user_org)
    return {
            "status": "success",
            "message": "Organisation created successfully",
            "data": {
                "orgId": db_org.orgId, 
                "name": db_org.name, 
                "description": db_org.description
            }
        }

@app.get("/api/organisations/{orgId}")
def get_organisation(orgId: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    organisation = db.query(models.Organisation).filter(models.Organisation.orgId == orgId).first()
    if organisation is None:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return {
            "status": "success",
            "message": "Organisation created successfully",
            "data": {
                "orgId": organisation.orgId, 
                "name": organisation.name, 
                "description": organisation.description
            }
        }

@app.post("/api/organisations/{orgId}/users")
def add_user_to_organisation(orgId: str, user: schemas.UserOrgs, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_org = db.query(models.Organisation).filter(models.Organisation.orgId == orgId, models.Organisation.creator_id == current_user.userId).first()
    if db_org is None:
        raise NotFoundError(
            detail="Organisation not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    db_user_org = schemas.UserOrgsCreate(userId=user.userId, orgId=db_org.orgId)
    organisations = db.query(models.User_organisation).filter(models.User_organisation.userId == user.userId, models.User_organisation.orgId == orgId).first()
    if user.userId == db_org.creator_id or organisations is not None:
        raise AuthError(
            detail="User already belongs to organisation",
            headers={"WWW-Authenticate": "Bearer"},
        )
    crud.create_user_orgs(db=db, data=db_user_org)
    return {
        "status": "success",
        "message": "User added to organisation successfully"
    }