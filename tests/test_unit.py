import pytest
from unittest.mock import Mock
from app.services.auth_service import AuthService
from app.utilities.security import encrypt_password, verify_password
from app.services.property_service import PropertyService 
from datetime import date
from app.services.booking_service import BookingService 
from app.services.review_service import ReviewService

def test_register_invalid_role():
    fake_repo = Mock()
    service = AuthService(fake_repo)

    with pytest.raises(ValueError) as error:
        service.register_user("mel", "mypass", "admin")

    assert str(error.value) == "Choose either the student or owner role"
    fake_repo.create.assert_not_called()

def test_encrypt_password():
    encrypted = encrypt_password("mypass")
    assert encrypted != "mypass"


def test_check_password():
    encrypted = encrypt_password("mypass")
    assert verify_password("mypass", encrypted) == True


def test_check_wrong_password():
    encrypted = encrypt_password("mypass")
    assert verify_password("wrongpass", encrypted) == False

def test_authenticate_wrong_password():
    fake_user = Mock()
    fake_user.id = 1
    fake_user.role = "owner"
    fake_user.password = encrypt_password("bobpass")

    fake_repo = Mock()
    fake_repo.get_by_username.return_value = fake_user

    service = AuthService(fake_repo)
    token = service.authenticate_user("bob", "wrongpass")

    assert token is None

def test_authenticate_success():
    fake_user = Mock()
    fake_user.id = 1
    fake_user.role = "owner"
    fake_user.password = encrypt_password("bobpass")

    fake_repo = Mock()
    fake_repo.get_by_username.return_value = fake_user

    service = AuthService(fake_repo)
    token = service.authenticate_user("bob", "bobpass")

    assert token is not None

def test_create_property_owner():
    fake_repo = Mock()
    service = PropertyService(fake_repo)

    service.create_property(
        owner_id=1,
        owner_role="owner",
        title=" Cozy Studio ",
        location="Watts Street",
        property_type="studio",
        description="Near campus",
        price=1200,
    )

    saved = fake_repo.create.call_args[0][0]
    assert saved.title == "Cozy Studio"


def test_create_property_not_owner():
    property_repo = Mock()
    service = PropertyService(property_repo)

    with pytest.raises(ValueError, match="Only owners can create properties"):
        service.create_property(
            owner_id=7, owner_role="student", title="Cozy Studio",
            location="Watts Street", property_type="studio",
            description="Near campus", price=1200,
        )

    property_repo.create.assert_not_called()


def test_search_price_bands():
    fake_repo = Mock()
    service = PropertyService(fake_repo)

    service.search_properties(price_range="under-1500")
    under = fake_repo.search.call_args.kwargs
    assert under["max_price"] == 1500
    assert under["max_price_exclusive"] == True

    service.search_properties(price_range="1500-2500")
    middle = fake_repo.search.call_args.kwargs
    assert middle["min_price"] == 1500
    assert middle["max_price"] == 2500
    assert middle["min_price_exclusive"] == False
    assert middle["max_price_exclusive"] == False

    service.search_properties(price_range="over-2500")
    over = fake_repo.search.call_args.kwargs
    assert over["min_price"] == 2500
    assert over["min_price_exclusive"] == True

def test_create_booking_bad_dates():
    fake_repo = Mock()
    service = BookingService(fake_repo)

    with pytest.raises(ValueError) as error:
        service.create_booking(
            property_id=1,
            student_id=2,
            check_in=date(2026, 12, 10),
            check_out=date(2026, 12, 5),
            notes="Hello",
        )

    assert str(error.value) == "Check-out must be after check-in"
    fake_repo.create.assert_not_called()

def test_create_booking_valid():
    fake_repo = Mock()
    service = BookingService(fake_repo)

    service.create_booking(
        property_id=1,
        student_id=2,
        check_in=date(2026, 12, 1),
        check_out=date(2026, 12, 10),
        notes="Hello",
    )

    saved = fake_repo.create.call_args[0][0]
    assert saved.status == "pending"

def test_confirm_booking_not_owner():
    fake_booking = Mock()
    fake_booking.property.owner_id = 1
    fake_booking.status = "pending"

    fake_repo = Mock()
    fake_repo.get_by_id.return_value = fake_booking

    service = BookingService(fake_repo)

    with pytest.raises(ValueError) as error:
        service.confirm_booking(booking_id=1, owner_id=99)

    assert str(error.value) == "You can only confirm your own bookings"
    fake_repo.update.assert_not_called()

def test_confirm_booking_pending():
    fake_booking = Mock()
    fake_booking.property.owner_id = 1
    fake_booking.status = "pending"

    fake_repo = Mock()
    fake_repo.get_by_id.return_value = fake_booking

    service = BookingService(fake_repo)
    service.confirm_booking(booking_id=1, owner_id=1)

    assert fake_booking.status == "confirmed"
    fake_repo.update.assert_called_once()

def test_reject_booking_not_pending():
    fake_booking = Mock()
    fake_booking.property.owner_id = 1
    fake_booking.status = "confirmed"

    fake_repo = Mock()
    fake_repo.get_by_id.return_value = fake_booking

    service = BookingService(fake_repo)

    with pytest.raises(ValueError) as error:
        service.reject_booking(booking_id=1, owner_id=1)

    assert str(error.value) == "Only pending requests can be rejected"
    fake_repo.update.assert_not_called()

def test_submit_review_duplicate():
    fake_repo = Mock()
    fake_repo.get_by_booking.return_value = Mock()

    service = ReviewService(fake_repo)

    with pytest.raises(ValueError) as error:
        service.submit_review(
            booking_id=1,
            property_id=1,
            reviewer_id=2,
            rating=5,
            comment="Great",
            reviewer_name="Sam",
            student_id="816000000",
        )

    assert str(error.value) == "This booking has already been reviewed"
    fake_repo.create.assert_not_called()