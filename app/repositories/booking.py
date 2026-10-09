from __future__ import annotations

from typing import Optional

from sqlmodel import Session, select

from app.models.property import Property
from app.models.booking import Booking, BookingBase


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, booking_data: BookingBase) -> Booking:
        booking_db = Booking.model_validate(booking_data)
        self.db.add(booking_db)
        self.db.commit()
        self.db.refresh(booking_db)
        return booking_db

    def get_by_id(self, booking_id: int) -> Optional[Booking]:
        return self.db.get(Booking, booking_id)

    def list_for_student(self, student_id: int) -> list[Booking]:
        return self.db.exec(
            select(Booking).where(Booking.student_id == student_id).order_by(Booking.id.desc())
        ).all()

    def list_for_owner(self, owner_id: int) -> list[Booking]:
        statement = select(Booking).join(Property).where(Property.owner_id == owner_id)
        return self.db.exec(statement.order_by(Booking.id.desc())).all()

    def list_pending_for_owner(self, owner_id: int) -> list[Booking]:
        statement = (
            select(Booking)
            .join(Property)
            .where(Property.owner_id == owner_id, Booking.status == "pending")
        )
        return self.db.exec(statement.order_by(Booking.id.desc())).all()

    def update(self, booking: Booking) -> Booking:
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
