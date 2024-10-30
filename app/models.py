
from typing import Optional
from sqlmodel import Field, Relationship, SQLModel


class Booking(SQLModel, table=True):
    classroom_id: int | None = Field(default=None, foreign_key="classroom.id", primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    
class Classroom(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    size: int
    level: int
    type: str
    booked: bool = Field(default=False)
    users: list["User"] = Relationship(back_populates="classrooms", link_model=Booking)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    classrooms: list[Classroom] = Relationship(back_populates="users", link_model=Booking)