from sqlmodel import Session
from models import Classroom, User
from db.dbCondig import engine

def seed():
    with Session(engine) as session:
        classroom1 = Classroom(name="A101", type="Studio", level=1, booked=False, size=20)
        classroom2 = Classroom(name="B101", type="Studio", level=2, booked=True, size=10)

        user1 = User(email="user1@test.com", username="user1", password="password", classroom_id=[classroom2])
          
       

        session.add(classroom1)
        session.add(classroom2)
        session.add(user1)
        session.commit()
        session.refresh(user1)