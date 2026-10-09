from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.review import Review
    from app.models.user import User


class PropertyBase(SQLModel):
    title: str = Field(index=True)
    location: str = Field(index=True)
    property_type: str = Field(default="studio", index=True)
    description: str = Field(default="")
    price: float = Field(default=0.0, ge=0, index=True)
    owner_id: int = Field(foreign_key="user.id", index=True)


class Property(PropertyBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    owner: Optional["User"] = Relationship(back_populates="properties")
    bookings: list["Booking"] = Relationship(back_populates="property")
    reviews: list["Review"] = Relationship(back_populates="property")
