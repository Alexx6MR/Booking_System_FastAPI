from fastapi import HTTPException, Request

from utils.constants import EMAIL_ADDRESS, EMAIL_BODY, EMAIL_SUBJECT, GITHUB_REPO
from utils.validation import is_valid_email


def error_handler(request: Request, templates, user, user_exists):
    accept_header = request.headers.get('accept')
    errors = []
    
    if 'text/html' in accept_header:
        return templates.TemplateResponse("register_page.html", {
            "request": request,
            "errors": errors
        })
    else:
        if not user.email.strip():
            raise HTTPException(status_code=400, detail="Email field cannot be empty")
        if not user.username.strip():
            raise HTTPException(status_code=400, detail="Username field cannot be empty")
        if not user.password.strip():
            raise HTTPException(status_code=400, detail="Password field cannot be empty")

        if not is_valid_email(user.email):
            raise HTTPException(status_code=400, detail="Invalid email format")
    
        if user_exists:
            raise HTTPException(status_code=400, detail="Username already exists")
        
def template_auth_error_handler(templates, request: Request, route:str , error_template_messsage: str, error_messsage: str, status_code:int):
    accept_header = request.headers.get('accept')
    if 'text/html' in accept_header:
        return templates.TemplateResponse(route, {"request": request,  
                "email_address": EMAIL_ADDRESS,
                "email_subject": EMAIL_SUBJECT,
                "email_body": EMAIL_BODY,
                "github_repo": GITHUB_REPO,
                "error": error_template_messsage
        })
    raise HTTPException(status_code=status_code, detail=error_messsage)