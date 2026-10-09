from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.property import Property
    from app.models.user import User


class ReviewBase(SQLModel):
    property_id: int = Field(foreign_key="property.id", index=True)
    booking_id: int = Field(foreign_key="booking.id", index=True, unique=True)
    reviewer_id: int = Field(foreign_key="user.id", index=True)
    rating: int = Field(default=5, ge=1, le=5)
    comment: str = Field(default="")
    reviewer_name: str 
    student_id: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )


class Review(ReviewBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    property: Optional["Property"] = Relationship(back_populates="reviews")
    booking: Optional["Booking"] = Relationship(back_populates="review")
    reviewer: Optional["User"] = Relationship(back_populates="reviews")
