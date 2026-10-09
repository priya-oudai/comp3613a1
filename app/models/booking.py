from datetime import date
from typing import TYPE_CHECKING, Optional

from pydantic import field_validator
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.property import Property
    from app.models.review import Review
    from app.models.user import User


class BookingBase(SQLModel):
    property_id: int = Field(foreign_key="property.id", index=True)
    student_id: int = Field(foreign_key="user.id", index=True)
    check_in: date
    check_out: date
    notes: str = Field(default="")
    request_date: date = Field(default_factory=date.today)
    status: str = Field(default="pending")

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in ["pending", "confirmed", "rejected"]:
            raise ValueError("Status must be 'pending', 'confirmed', or 'rejected'")
        return value


class Booking(BookingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    property: Optional["Property"] = Relationship(back_populates="bookings")
    student: Optional["User"] = Relationship(back_populates="bookings")
    review: Optional["Review"] = Relationship(back_populates="booking")
