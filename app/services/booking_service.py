from __future__ import annotations

from datetime import date

from app.models.booking import BookingBase
from app.repositories.booking import BookingRepository


class BookingService:
    def __init__(self, booking_repo: BookingRepository):
        self.booking_repo = booking_repo

    def create_booking(
        self,
        property_id: int,
        student_id: int,
        check_in: date,
        check_out: date,
        notes: str,
    ):
        if check_in >= check_out:
            raise ValueError("Check-out must be after check-in")
        return self.booking_repo.create(
            BookingBase(
                property_id=property_id,
                student_id=student_id,
                check_in=check_in,
                check_out=check_out,
                notes=notes.strip(),
                status="pending",
            )
        )

    def confirm_booking(self, booking_id: int, owner_id: int):
        booking = self.booking_repo.get_by_id(booking_id)
        if booking is None:
            raise ValueError("Booking not found")
        if booking.property.owner_id != owner_id:
            raise ValueError("You can only confirm your own bookings")
        if booking.status == "confirmed":
            return booking
        if booking.status != "pending":
            raise ValueError("Only pending requests can be confirmed")
        booking.status = "confirmed"
        return self.booking_repo.update(booking)

    def list_student_bookings(self, student_id: int):
        return self.booking_repo.list_for_student(student_id)

    def list_owner_bookings(self, owner_id: int):
        return self.booking_repo.list_for_owner(owner_id)

    def list_pending_owner_bookings(self, owner_id: int):
        return self.booking_repo.list_pending_for_owner(owner_id)

    def reject_booking(self, booking_id: int, owner_id: int):
        booking = self.booking_repo.get_by_id(booking_id)
        if booking is None:
            raise ValueError("Booking not found")
        if booking.property.owner_id != owner_id:
            raise ValueError("You can only reject your own bookings")
        if booking.status != "pending":
            raise ValueError("Only pending requests can be rejected")
        booking.status = "rejected"
        return self.booking_repo.update(booking)
