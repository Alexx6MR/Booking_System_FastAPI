import ast
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import select
from utils.converter import time_to_integer
from utils.validation import time_validation
from models import Booking, Classroom, User
from db.dbConfig import SessionDep


# Creates an API router for handling authentication-related endpoints.
user_router = APIRouter()
# Defines the base directory path for the current file.(app/*)
BASE_DIR = Path(__file__).resolve().parent.parent
# Sets up Jinja2 template rendering using the 'templates' directory.
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Get All Users Bookings
@user_router.get("/{user_id}/bookings")
def get_user_bookings(request: Request, user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    accept_header = request.headers.get('accept')
    global_context = request.state.global_context
     
    if not user:    
        raise HTTPException(status_code=404, detail="User not found")

    bookings_statement = select(Booking).where(Booking.user_id == user_id)
    bookings = session.exec(bookings_statement).all()
    bookings_data = []
    
    
    for booking in bookings:
        classroom = session.get(Classroom, booking.classroom_id)
        if classroom:
            booking_info = {
                "booking_id": booking.id,
                "classroom_id": classroom.id,
                "classroom_level": classroom.level,
                "classroom_name": classroom.name, 
                "start_time": booking.start_time.isoformat(),
                "end_time": booking.end_time.isoformat()
            }
            bookings_data.append(booking_info)
    
    
    
    if 'text/html' in accept_header:
        return templates.TemplateResponse("pages/user/user_booking_page.html", {"request": request, "bookingsList": bookings_data, "is_logged_in": global_context["is_logged_in"], "user_id": int(global_context["user_id"]), "time_to_integer": time_to_integer})
        
    return JSONResponse(content=bookings_data)

# Get Users Update Bookings Page
@user_router.get("/{user_id}/update/{classroom_id}")
def get_user_update(request: Request, user_id: int, classroom_id: int, session: SessionDep):
    classroom = session.get(Classroom, classroom_id)
    
    # Retrieves the 'accept' header from the request to determine the desired response format.
    accept_header = request.headers.get('accept')
     # Acceder al contexto global
    global_context = request.state.global_context
    
    # Checks if the classroom object is None, indicating it was not found in the database.    
    if not classroom: 
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    
    # Define available times from 8:00 AM to 6:00 PM
    timeslots = []
    start_time = datetime.strptime("08:00:00", "%H:%M:%S").time()
    end_time = datetime.strptime("18:00:00", "%H:%M:%S").time()
    
    #Current will change but start_time will be the same
    current_time = start_time

    # Get all bookings for the classroom
    bookings_statement = select(Booking).where(Booking.classroom_id == classroom_id)
    bookings = session.exec(bookings_statement).all()

    # Iterates through each hour between the start and end times to generate timeslots.
    while current_time < end_time:
        # Calculates the next hour time for the current timeslot.
        next_time = (datetime.combine(datetime.today(), current_time) + timedelta(hours=1)).time()
        # Determines if the current timeslot is available by checking against existing bookings.
        is_available = not any(
            booking.start_time <= current_time < booking.end_time for booking in bookings
        )
        
        is_user = not any(
            booking.user_id == user_id and is_available for booking in bookings
        )
        
        # Appends the current timeslot as a dictionary to the timeslots list, including start, end times, and availability.
        timeslots.append({
            "start_time": current_time.isoformat(),
            "end_time": next_time.isoformat(),
            "available": is_available,
            "isFromUser": is_user
        })
        # Moves to the next hour for the next iteration of the timeslot generation.
        current_time = next_time
    
    # Converts the classroom object to a dictionary representation.
    classroom_data = classroom.model_dump()
    # Adds the generated timeslots to the classroom data dictionary.
    classroom_data["timeslots"] = timeslots
    
    
    # this is for html
    if 'text/html' in accept_header:
        return templates.TemplateResponse("pages/user/user_edit_booking_page.html", {"request": request, "classroom": classroom_data, "user_id": global_context["user_id"], "is_logged_in": global_context["is_logged_in"], "time_to_integer": time_to_integer})
    
    #This is for Curl or Swagger
    return JSONResponse(content=classroom_data)

# Create booking
@user_router.post("/{user_id}/create")
def book_timeslot(request: Request, session: SessionDep, user_id: int, classroom_id: int = Form(...), timeslot_ids: List = Form(None),):
    classroom = session.get(Classroom, classroom_id)

    if not classroom:
        raise HTTPException(status_code=404, detail="Classroom not found")
    
    accept_header = request.headers.get('accept')
    
    if timeslot_ids is None:
        timeslot_ids = [] 
    
    bookings_list = []
     # Validate and convert the start and end time strings to time objects
    for time in timeslot_ids:
        # Convert the string (which looks like a dictionary) to an actual dictionary
        try:
            new_slot = ast.literal_eval(time)
        except (ValueError, SyntaxError):
            raise HTTPException(status_code=400, detail="Invalid timeslot format")

        # Convert start_time and end_time to datetime.time objects for insertion
        try:
            start_time = datetime.strptime(new_slot["start_time"], "%H:%M:%S").time()
            end_time = datetime.strptime(new_slot["end_time"], "%H:%M:%S").time()
        except KeyError:
            raise HTTPException(status_code=400, detail="Timeslot must contain 'start_time' and 'end_time'")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format for start or end time. Use 'HH:MM:SS'.")

        # Check if the timeslot is available
        bookings_statement = select(Booking).where(
            (Booking.classroom_id == classroom_id) &
            (Booking.start_time < start_time) &
            (Booking.end_time > end_time)
        )
        overlapping_bookings = session.exec(bookings_statement).all()
        if overlapping_bookings:
            raise HTTPException(status_code=400, detail=f"Timeslot from {start_time} to {end_time} is already booked")

        # Create a new booking
        new_booking = Booking(
            classroom_id=classroom_id,
            user_id=user_id,
            start_time=start_time,  # Ensure this is a time object
            end_time=end_time        # Ensure this is a time object
        )

        # Add the new booking to the session
        session.add(new_booking)
        session.commit()  # Commit each booking

        # Refresh the booking to get the ID and other database-assigned values
        session.refresh(new_booking)

        # Convert the booking to a dictionary for JSON serialization
        bookings_list.append({
            "booking_id": new_booking.id,
            "classroom_id": new_booking.classroom_id,
            "user_id": new_booking.user_id,
            "start_time": new_booking.start_time.isoformat(),
            "end_time": new_booking.end_time.isoformat()
        })

    return JSONResponse(content={
        "message": "Booking created successfully",
        "bookings": bookings_list
    })

# Update Booking
@user_router.put("/{user_id}/update/{classroom_id}")
def edit_booking(request: Request, session: SessionDep, classroom_id: int, user_id: int, booking_id: int, timeslot_ids: List = Form(None) ):
    booking = session.get(Booking, booking_id)
    
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if timeslot_ids is None:
        timeslot_ids = [] 
    # Validates and converts the start and end time strings to time objects using the time_validation function.
    
    bookings_list = []
     # Validate and convert the start and end time strings to time objects
    for time in timeslot_ids:
        # Convert the string (which looks like a dictionary) to an actual dictionary
        try:
            new_slot = ast.literal_eval(time)
        except (ValueError, SyntaxError):
            raise HTTPException(status_code=400, detail="Invalid timeslot format")

        # Convert start_time and end_time to datetime.time objects for insertion
        try:
            start_time = datetime.strptime(new_slot["start_time"], "%H:%M:%S").time()
            end_time = datetime.strptime(new_slot["end_time"], "%H:%M:%S").time()
        except KeyError:
            raise HTTPException(status_code=400, detail="Timeslot must contain 'start_time' and 'end_time'")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid time format for start or end time. Use 'HH:MM:SS'.")

        # Check if the timeslot is available
        bookings_statement = select(Booking).where(
            (Booking.classroom_id == classroom_id) &
            (Booking.start_time < start_time) &
            (Booking.end_time > end_time)
        )
        overlapping_bookings = session.exec(bookings_statement).all()
        
        if overlapping_bookings:
            raise HTTPException(status_code=400, detail=f"Timeslot from {start_time} to {end_time} is already booked")

        # Create a new booking
        new_booking = Booking(
            classroom_id=classroom_id,
            user_id=user_id,
            start_time=start_time,  # Ensure this is a time object
            end_time=end_time        # Ensure this is a time object
        )

        # Add the new booking to the session
        session.add(new_booking)
        session.commit()  # Commit each booking

        # Refresh the booking to get the ID and other database-assigned values
        session.refresh(new_booking)

        # Convert the booking to a dictionary for JSON serialization
        bookings_list.append({
            "booking_id": new_booking.id,
            "classroom_id": new_booking.classroom_id,
            "user_id": new_booking.user_id,
            "start_time": new_booking.start_time.isoformat(),
            "end_time": new_booking.end_time.isoformat()
        })

    return JSONResponse(content={
        "message": "Booking created successfully",
        "bookings": bookings_list
    })

# Delete booking
@user_router.delete("/{user_id}/delete/{booking_id}")
def delete_booking(user_id: int, booking_id: int, session: SessionDep):
    booking = session.get(Booking, booking_id)
    if not booking or booking.user_id != user_id:
        raise HTTPException(status_code=404, detail="Booking not found")

    session.delete(booking)
    session.commit()

    return JSONResponse(content={
        "message": "Booking deleted successfully",
        "booking_id": booking_id
    })
