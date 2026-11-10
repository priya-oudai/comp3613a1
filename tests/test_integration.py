from sqlmodel import SQLModel, Session, create_engine

import app.models.user
import app.models.property
import app.models.booking
import app.models.review
import pytest
from app.repositories.user import UserRepository
from app.services.auth_service import AuthService
from sqlalchemy.exc import IntegrityError
from app.repositories.property import PropertyRepository
from app.services.property_service import PropertyService
from datetime import date
from app.repositories.booking import BookingRepository
from app.services.booking_service import BookingService
from app.repositories.review import ReviewRepository
from app.services.review_service import ReviewService
from fastapi.testclient import TestClient
from app.main import app

def make_test_session():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    return Session(engine)


def test_register_and_authenticate():
    session = make_test_session()
    userRepo = UserRepository(session)
    service = AuthService(userRepo)

    newUser = service.register_user("mel", "mypass", "student")
    token = service.authenticate_user("mel", "mypass")

    assert newUser.id is not None
    assert newUser.password != "mypass"
    assert token is not None

def test_duplicate_username():
    session = make_test_session()
    user_repo = UserRepository(session)
    service = AuthService(user_repo)

    service.register_user("mel", "mypass", "student")

    with pytest.raises(IntegrityError):
        service.register_user("mel", "otherpass", "owner")

def test_create_property_persists():
    session = make_test_session()
    auth_service = AuthService(UserRepository(session))
    property_repo = PropertyRepository(session)
    property_service = PropertyService(property_repo)

    owner = auth_service.register_user("bob", "bobpass", "owner")
    created = property_service.create_property(
        owner_id=owner.id,
        owner_role="owner",
        title="Cozy Studio",
        location="Watts Street",
        property_type="studio",
        description="Near campus",
        price=1200,
    )

    found = property_repo.get_by_id(created.id)

    assert found is not None
    assert found.title == "Cozy Studio"
    assert found.owner_id == owner.id
    assert found.price == 1200

def test_list_owner_properties():
    session = make_test_session()
    auth_service = AuthService(UserRepository(session))
    property_service = PropertyService(PropertyRepository(session))

    bob = auth_service.register_user("bob", "bobpass", "owner")
    ken = auth_service.register_user("ken", "kenpass", "owner")

    property_service.create_property(
        owner_id=bob.id,
        owner_role="owner",
        title="Maxton Studio",
        location="Watts Street",
        property_type="studio",
        description="5 minute from campus",
        price=1200,
    )
    property_service.create_property(
        owner_id=ken.id,
        owner_role="owner",
        title="Belrose Flat",
        location="St Augustine Street",
        property_type="Apartment",
        description="Great shared apartment for students with 2 bedrooms and 1 bathroom",
        price=1800,
    )

    bobs_properties = property_service.list_owner_properties(bob.id)

    assert len(bobs_properties) == 1
    assert bobs_properties[0].title == "Maxton Studio"
    assert bobs_properties[0].owner_id == bob.id

def test_search_filters():
    session = make_test_session()
    auth_service = AuthService(UserRepository(session))
    property_service = PropertyService(PropertyRepository(session))

    owner = auth_service.register_user("bob", "bobpass", "owner")

    property_service.create_property(
        owner_id=owner.id,
        owner_role="owner",
        title="High school Studio",
        location="Watts Street",
        property_type="studio",
        description="Near campus and affordable for students with a budget of $1000",
        price=1000,
    )
    property_service.create_property(
        owner_id=owner.id,
        owner_role="owner",
        title="apartment",
        location="Old Tim Road",
        property_type="apartment",
        description="Near campus",
        price=1500,
    )
    property_service.create_property(
        owner_id=owner.id,
        owner_role="owner",
        title="Study House",
        location="Gordon Street",
        property_type="studio",
        description="Best studio for students with a kitchen and a bathroom",
        price=2600,
    )

    under = property_service.search_properties(price_range="under-1500")
    middle = property_service.search_properties(price_range="1500-2500")
    over = property_service.search_properties(price_range="over-2500")
    by_title = property_service.search_properties(query="Study")
    by_location = property_service.search_properties(query="Old Tim")

    assert len(under) == 1
    assert under[0].price == 1000

    assert len(middle) == 1
    assert middle[0].price == 1500

    assert len(over) == 1
    assert over[0].price == 2600

    assert len(by_title) == 1
    assert by_title[0].title == "Study House"

    assert len(by_location) == 1
    assert by_location[0].title == "apartment"

def test_booking_created_pending():
    session = make_test_session()
    auth_service = AuthService(UserRepository(session))
    property_service = PropertyService(PropertyRepository(session))
    booking_service = BookingService(BookingRepository(session))

    owner = auth_service.register_user("bob", "bobpass", "owner")
    student = auth_service.register_user("mel", "mypass", "student")
    listing = property_service.create_property(
        owner_id=owner.id,
        owner_role="owner",
        title="Cozy Studio",
        location="Watts Street",
        property_type="studio",
        description="Near campus",
        price=1200,
    )

    booking = booking_service.create_booking(
        property_id=listing.id,
        student_id=student.id,
        check_in=date(2026, 11, 4),
        check_out=date(2026, 11, 10),
        notes="Hello, I would like to book this property",
    )

    student_bookings = booking_service.list_student_bookings(student.id)
    pending_bookings = booking_service.list_pending_owner_bookings(owner.id)

    assert booking.status == "pending"
    assert len(student_bookings) == 1
    assert student_bookings[0].id == booking.id
    assert len(pending_bookings) == 1
    assert pending_bookings[0].id == booking.id

def test_confirm_booking():
    session = make_test_session()
    auth_service = AuthService(UserRepository(session))
    property_service = PropertyService(PropertyRepository(session))
    booking_repo = BookingRepository(session)
    booking_service = BookingService(booking_repo)

    owner = auth_service.register_user("bob", "bobpass", "owner")
    student = auth_service.register_user("mel", "mypass", "student")
    listing = property_service.create_property(
        owner_id=owner.id,
        owner_role="owner",
        title="Cozy Studio",
        location="Watts Street",
        property_type="studio",
        description="Near campus",
        price=1200,
    )
    booking = booking_service.create_booking(
        property_id=listing.id,
        student_id=student.id,
        check_in=date(2026, 11, 1),
        check_out=date(2026, 11, 10),
        notes="Hello, I would like to book this property",
    )

    booking_service.confirm_booking(booking_id=booking.id, owner_id=owner.id)

    saved_booking = booking_repo.get_by_id(booking.id)
    pending_bookings = booking_service.list_pending_owner_bookings(owner.id)

    assert saved_booking.status == "confirmed"
    assert len(pending_bookings) == 0

def test_reject_booking():
    session = make_test_session()
    auth_service = AuthService(UserRepository(session))
    property_service = PropertyService(PropertyRepository(session))
    booking_repo = BookingRepository(session)
    booking_service = BookingService(booking_repo)

    owner = auth_service.register_user("bob", "bobpass", "owner")
    student = auth_service.register_user("mel", "mypass", "student")
    listing = property_service.create_property(
        owner_id=owner.id,
        owner_role="owner",
        title="Cozy Studio",
        location="Watts Street",
        property_type="studio",
        description="Near campus",
        price=1200,
    )
    booking = booking_service.create_booking(
        property_id=listing.id,
        student_id=student.id,
        check_in=date(2026, 12, 1),
        check_out=date(2026, 12, 10),
        notes="Hello",
    )

    booking_service.reject_booking(booking_id=booking.id, owner_id=owner.id)

    saved_booking = booking_repo.get_by_id(booking.id)
    pending_bookings = booking_service.list_pending_owner_bookings(owner.id)

    assert saved_booking.status == "rejected"
    assert len(pending_bookings) == 0

def test_review_persists():
    session = make_test_session()
    auth_service = AuthService(UserRepository(session))
    property_service = PropertyService(PropertyRepository(session))
    booking_service = BookingService(BookingRepository(session))
    review_service = ReviewService(ReviewRepository(session))

    owner = auth_service.register_user("bob", "bobpass", "owner")
    student = auth_service.register_user("mel", "mypass", "student")
    listing = property_service.create_property(
        owner_id=owner.id,
        owner_role="owner",
        title="Cozy Studio",
        location="Watts Street",
        property_type="studio",
        description="Near campus",
        price=1200,
    )
    booking = booking_service.create_booking(
        property_id=listing.id,
        student_id=student.id,
        check_in=date(2026, 12, 1),
        check_out=date(2026, 12, 10),
        notes="Hello",
    )

    review = review_service.submit_review(
        booking_id=booking.id,
        property_id=listing.id,
        reviewer_id=student.id,
        rating=5,
        comment="Great place",
        reviewer_name="Mel",
        student_id="816000000",
    )

    property_reviews = review_service.list_property_reviews(listing.id)

    assert review.id is not None
    assert review.booking_id == booking.id
    assert len(property_reviews) == 1
    assert property_reviews[0].comment == "Great place"
    assert property_reviews[0].rating == 5

def test_one_review_per_booking():
    session = make_test_session()
    auth_service = AuthService(UserRepository(session))
    property_service = PropertyService(PropertyRepository(session))
    booking_service = BookingService(BookingRepository(session))
    review_service = ReviewService(ReviewRepository(session))

    owner = auth_service.register_user("bob", "bobpass", "owner")
    student = auth_service.register_user("mel", "mypass", "student")
    listing = property_service.create_property(
        owner_id=owner.id,
        owner_role="owner",
        title="Cozy Studio",
        location="Watts Street",
        property_type="studio",
        description="Near campus",
        price=1200,
    )
    booking = booking_service.create_booking(
        property_id=listing.id,
        student_id=student.id,
        check_in=date(2026, 12, 1),
        check_out=date(2026, 12, 10),
        notes="Hello",
    )

    review_service.submit_review(
        booking_id=booking.id,
        property_id=listing.id,
        reviewer_id=student.id,
        rating=5,
        comment="Great place",
        reviewer_name="Mel",
        student_id="816000000",
    )

    with pytest.raises(ValueError, match="This booking has already been reviewed"):
        review_service.submit_review(
            booking_id=booking.id,
            property_id=listing.id,
            reviewer_id=student.id,
            rating=3,
            comment="Second try",
            reviewer_name="Mel",
            student_id="816000000",
        )

    property_reviews = review_service.list_property_reviews(listing.id)
    assert len(property_reviews) == 1

def test_protected_route_requires_login():
    client = TestClient(app)

    response = client.get("/properties/new", follow_redirects=False)

    assert response.status_code == 401