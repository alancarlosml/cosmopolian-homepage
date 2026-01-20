from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os

import models, schemas, database
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Security Config
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 day

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cosmopolian Contact API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

# Create a router for all API endpoints
api_router = APIRouter()

# Auth Endpoints
@api_router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Temporary endpoint to create first admin (should be removed or secured)
@api_router.post("/setup-admin", response_model=schemas.UserResponse)
def setup_admin(db: Session = Depends(get_db)):
    admin = db.query(models.User).filter(models.User.username == "admin").first()
    if admin:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    new_admin = models.User(
        username="admin",
        hashed_password=get_password_hash("admin123") # Change this immediately!
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

# Contact Endpoints
@api_router.post("/contacts/", response_model=schemas.ContactResponse)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = models.Contact(
        name=contact.name,
        company=contact.company,
        email=contact.email,
        message=contact.message
    )
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

@api_router.get("/contacts/", response_model=List[schemas.ContactResponse])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    contacts = db.query(models.Contact).order_by(models.Contact.created_at.desc()).offset(skip).limit(limit).all()
    return contacts

# Define root on the main app or the router
@api_router.get("/")
def read_root():
    return {"message": "Welcome to Cosmopolian Contact API"}

# Include the router with the /api prefix
app.include_router(api_router, prefix="/api")

@app.get("/")
def main_root():
    return {"message": "Cosmopolian API Root. Use /api for endpoints."}
