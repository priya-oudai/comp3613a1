from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.property import Property
    from app.models.review import Review


class UserBase(SQLModel):
    username: str = Field(index=True, unique=True)
    password: str
    role: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    properties: list["Property"] = Relationship(back_populates="owner")
    bookings: list["Booking"] = Relationship(back_populates="student")
    reviews: list["Review"] = Relationship(back_populates="reviewer")