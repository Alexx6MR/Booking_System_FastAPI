
from datetime import time


class Classroom:
    id: int
    name: str
    type: str
    level: int
    size: int
    image_url: str  # URL of the classroom image
    bookings: list
    
# Represents the User table with fields for email, username, password, and related bookings.
class User:
    id: int
    email: str
    username: str
    password: str
    bookings: list

# Represents the Booking table with fields for user, classroom, start time, end time, and relationships to User and Classroom.
class Booking:
    id: int
    user_id: int
    classroom_id: int
    start_time: time
    end_time: time
    user: User
    classroom: Classroom
