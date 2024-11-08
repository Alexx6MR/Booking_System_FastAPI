from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from models import User
from db.dbConfig import SessionDep
from passlib.context import CryptContext
from utils.constants import EMAIL_ADDRESS, EMAIL_BODY, EMAIL_SUBJECT, GITHUB_REPO
from utils.error_handler import template_auth_error_handler
from utils.validation import is_valid_email


# Creates an API router for handling authentication-related endpoints.
auth_router = APIRouter()

# Defines the base directory path for the current file.(app/*)
BASE_DIR = Path(__file__).resolve().parent.parent

# Sets up Jinja2 template rendering using the 'templates' directory.
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Configures the password hashing context using the bcrypt algorithm.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashes a given password using the configured password hashing context.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Login route
@auth_router.get("/login")
def show_login(request: Request):
    return templates.TemplateResponse("pages/auth/login_page.html", {"request": request,  
        "email_address": EMAIL_ADDRESS,
        "email_subject": EMAIL_SUBJECT,
        "email_body": EMAIL_BODY,
        "github_repo": GITHUB_REPO,
        })

@auth_router.post("/login")
def process_login(request: Request,session: SessionDep, email: str = Form(...), password: str = Form(...)):
    accept_header = request.headers.get('accept')
    
    if not is_valid_email(email):
        return template_auth_error_handler(
            request=request,
            templates=templates,
            route="pages/auth/login_page.html", 
            error_messsage="Invalid email format",
            error_template_messsage="Invalid email format",
            status_code=400
        )    
    
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return template_auth_error_handler(
            request=request,
            templates=templates,
            route="pages/auth/login_page.html", 
            error_messsage="User dont exits",
            error_template_messsage="User dont exits",
            status_code=401
        )    
    
    # Verify password
    if not pwd_context.verify(password, user.password):
        return template_auth_error_handler(
            request=request,
            templates=templates,
            route="pages/auth/login_page.html", 
            error_messsage="Incorrect password",
            error_template_messsage="Something went wrong try again",
            status_code=401
        )    
    
    response = RedirectResponse(url="/classrooms", status_code=302)
    response.set_cookie(key="session_token", value=email, httponly=True)
    response.set_cookie(key="user_id", value=user.id, httponly=True)
    
    if 'text/html' in accept_header:
        return response
   
    return  JSONResponse(content={
        "message": "Login successful",
        "user": {
            "id": user.id ,
            "username": user.username
        }
    })

# Register Route
@auth_router.get("/register")
def show_register(request: Request):
    return templates.TemplateResponse("pages/auth/register_page.html", {"request": request, 
        "email_address": EMAIL_ADDRESS,
        "email_subject": EMAIL_SUBJECT,
        "email_body": EMAIL_BODY,
        "github_repo": GITHUB_REPO,})


@auth_router.post("/register")
def create_user(request: Request, session: SessionDep, username: str = Form(...), password: str = Form(...), email: str = Form(...)):
    accept_header = request.headers.get('accept')
    
    if not is_valid_email(email):
        return template_auth_error_handler(
            request=request,
            templates=templates,
            route="pages/auth/register_page.html", 
            error_messsage="Invalid email format",
            error_template_messsage="Invalid email format",
            status_code=400
        )
        
    # Check if user already exists
    user_exists = session.exec(select(User).where(User.email == email)).first()
     
    if user_exists: 
        return template_auth_error_handler(
            request=request,
            templates=templates,
            route="pages/auth/register_page.html", 
            error_messsage="Username already exists",
            error_template_messsage="Username already exists",
            status_code=401
        )    

    # Create new user
    hashed_password = hash_password(password)
    new_user = User(username=username, password=hashed_password, email=email)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    response = RedirectResponse(url="/auth/login", status_code=302)
    
    if 'text/html' in accept_header:
        return response

    return JSONResponse(content={
        "message": "User created successfully",
        "user": {
            "from web": "existe" if user_exists else "No existe",
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email
        }
    })
    
@auth_router.get("/logout")
def logout(request: Request, response: Response):
    # Borrar la cookie de sesión
    accept_header = request.headers.get('accept')
    response = RedirectResponse(url="/classrooms", status_code=302)
    response.delete_cookie(key="session_token")
    response.delete_cookie(key="user_id")
    
    if 'text/html' in accept_header:
        return response
    
    return JSONResponse(content={
        "message": f"User {request.cookies.get("user_id")} logout successfully",
    })