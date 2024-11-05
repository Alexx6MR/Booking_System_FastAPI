from fastapi import HTTPException, Request

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