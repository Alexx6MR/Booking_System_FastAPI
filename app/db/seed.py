from sqlmodel import Session
from models import Booking, Classroom, User
from db.dbConfig import engine
from datetime import datetime


# Create fake data in the database.db
def seed():
    with Session(engine) as session:
        # Create fake classrooms
        classrooms = [
            Classroom(name="A101", type="Studio", level=1, size=20, image_url="/static/images/classrooms/classroom1.jpg"),
            Classroom(name="B202", type="Lecture Hall", level=2, size=50, image_url="/static/images/classrooms/classroom2.jpg"),
            Classroom(name="C303", type="Lab", level=3, size=30, image_url="/static/images/classrooms/classroom3.jpg"),
            Classroom(name="D404", type="alexei Room", level=4, size=15, image_url="/static/images/classrooms/classroom4.jpg"),
            Classroom(name="D404", type="martinez Room", level=3, size=40, image_url="/static/images/classrooms/classroom5.jpg"),
            Classroom(name="D404", type="rodriguez Room", level=1, size=10, image_url="/static/images/classrooms/classroom6.jpg"),
        ]

        # Add classrooms to the session
        session.add_all(classrooms)
        session.commit()

        # Create fake users
        users = [
            User(email="user1@example.com", username="user1", password="password1"),
        ]

        # Add users to the session
        session.add_all(users)
        session.commit()     
        
        # Create a booking for user1
        booking1 = Booking(
            classroom_id=classrooms[0].id,
            user_id=users[0].id,
            start_time=datetime.strptime("09:00:00", "%H:%M:%S").time(),
            end_time=datetime.strptime("10:00:00", "%H:%M:%S").time()
        )
        session.add(booking1)
        session.commit()