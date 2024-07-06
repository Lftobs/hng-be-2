from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional

class UserBase(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    userId: str
 
class UserOrgs(BaseModel):
    userId : str   

class OrganisationBase(BaseModel):
    name: str
    description: Optional[str] = None

class OrganisationCreate(OrganisationBase):
    pass

class OrganisationResponse(OrganisationBase):
    orgId: str

class UserOrgsCreate(BaseModel):
    userId: str
    orgId: str

class ErrorSchema(BaseModel):
    status: str
    message: str
    statusCode: int