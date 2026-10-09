from __future__ import annotations

from app.models.review import ReviewBase
from app.repositories.review import ReviewRepository


class ReviewService:
    def __init__(self, review_repo: ReviewRepository):
        self.review_repo = review_repo

    def submit_review(
        self,
        booking_id: int,
        property_id: int,
        reviewer_id: int,
        rating: int,
        comment: str,
        reviewer_name: str,
        student_id: str,
    ):
        cleaned_name = reviewer_name.strip()
        cleaned_student_id = student_id.strip()
        if not cleaned_name or not cleaned_student_id:
            raise ValueError("Reviewer name and student ID cannot be empty")
        if self.review_repo.get_by_booking(booking_id):
            raise ValueError("This booking has already been reviewed")
        return self.review_repo.create(
            ReviewBase(
                booking_id=booking_id,
                property_id=property_id,
                reviewer_id=reviewer_id,
                rating=rating,
                comment=comment.strip(),
                reviewer_name=cleaned_name,
                student_id=cleaned_student_id,
            )
        )

    def list_property_reviews(self, property_id: int):
        return self.review_repo.list_for_property(property_id)
