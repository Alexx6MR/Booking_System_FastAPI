from datetime import datetime
import re
from fastapi import HTTPException, Request



# Validate the time and raise Exceptions
def time_validation(start_time: str, end_time: str):
    # Validate time format
    try:
        start_time_obj = datetime.strptime(start_time.strip('\"'), "%H:%M:%S").time()
        end_time_obj = datetime.strptime(end_time.strip('\"'), "%H:%M:%S").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM:SS")
    
    # Check if end time is after start time
    if end_time_obj < start_time_obj:
        raise HTTPException(status_code=400, detail="End time must be after start time")
    
    # Check if times is differents
    if end_time_obj == start_time_obj:
        raise HTTPException(status_code=400, detail="Times must be different")
    
    # Ensure that start and end times are on the hour
    if start_time_obj.minute != 0 or start_time_obj.second != 0 or end_time_obj.minute != 0 or end_time_obj.second != 0:
        raise HTTPException(status_code=400, detail="Time must be on the hour, e.g., 10:00:00")
    
    return start_time_obj, end_time_obj


# Validate if the email is a valid email
def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

def authorized_user(request: Request, user_id:int):
    global_context = request.state.global_context
    is_logged_in = global_context["is_logged_in"]
    logged_user = global_context["user_id"] 
        
    
    if not is_logged_in:
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )

    elif int(logged_user) != int(user_id):
        raise HTTPException(
            status_code=401,
            detail="User not authenticated",
        )
    
    
    
    return [is_logged_in, logged_user]