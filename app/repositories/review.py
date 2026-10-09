from __future__ import annotations

from typing import Optional

from sqlmodel import Session, select

from app.models.review import Review, ReviewBase


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, review_data: ReviewBase) -> Review:
        review_db = Review.model_validate(review_data)
        self.db.add(review_db)
        self.db.commit()
        self.db.refresh(review_db)
        return review_db

    def get_by_booking(self, booking_id: int) -> Optional[Review]:
        return self.db.exec(select(Review).where(Review.booking_id == booking_id)).one_or_none()

    def list_for_property(self, property_id: int) -> list[Review]:
        return self.db.exec(
            select(Review).where(Review.property_id == property_id).order_by(Review.id.desc())
        ).all()
