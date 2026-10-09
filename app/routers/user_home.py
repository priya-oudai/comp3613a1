from __future__ import annotations

from datetime import date

from fastapi import Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.booking import BookingRepository
from app.repositories.property import PropertyRepository
from app.repositories.review import ReviewRepository
from app.services.booking_service import BookingService
from app.services.property_service import PropertyService
from app.services.review_service import ReviewService
from app.utilities.flash import flash
from . import router, templates


@router.get("/app", response_class=HTMLResponse, name="user_home_view")
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    query = request.query_params.get("q", "").strip()
    price_range = request.query_params.get("price", "").strip()
    property_type = request.query_params.get("type", "").strip()
    property_repo = PropertyRepository(db)
    property_service = PropertyService(property_repo)
    is_owner_view = user.role == "owner"
    my_listings = property_service.list_owner_properties(user.id) if is_owner_view else []
    published_property = None
    if is_owner_view:
        published_property_id = request.session.pop("published_property_id", None)
        if isinstance(published_property_id, int):
            candidate = property_service.get_property(published_property_id)
            if candidate is not None and candidate.owner_id == user.id:
                published_property = candidate
    if is_owner_view:
        properties = my_listings
    else:
        properties = property_service.search_properties(query, price_range, property_type)

    context = {
        "user": user,
        "properties": properties,
        "my_listings": my_listings,
        "published_property": published_property,
        "query": query,
        "price_range": price_range,
        "property_type_filter": property_type,
        "property_count": len(properties),
        "is_owner_view": is_owner_view,
    }
    return templates.TemplateResponse(request=request, name="app.html", context=context)


@router.get("/bookings", response_class=HTMLResponse, name="my_bookings_view")
async def my_bookings_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    if user.role == "owner":
        flash(request, "My bookings is available to student accounts.", "danger")
        return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)
    booking_service = BookingService(BookingRepository(db))
    return templates.TemplateResponse(
        request=request,
        name="my-bookings.html",
        context={"user": user, "bookings": booking_service.list_student_bookings(user.id)},
    )


@router.get("/owner/bookings", response_class=HTMLResponse, name="owner_booking_requests_view")
async def owner_booking_requests_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    if user.role != "owner":
        flash(request, "Only owners can view booking requests.", "danger")
        return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)
    booking_service = BookingService(BookingRepository(db))
    pending_bookings = booking_service.list_pending_owner_bookings(user.id)

    return templates.TemplateResponse(
        request=request,
        name="owner-bookings.html",
        context={"user": user, "pending_bookings": pending_bookings},
    )


@router.post("/owner/bookings/{booking_id}/status", response_class=HTMLResponse, name="owner_booking_status_action")
async def owner_booking_status_action(
    request: Request,
    booking_id: int,
    user: AuthDep,
    db: SessionDep,
    action: str = Form(...),
):
    if user.role != "owner":
        flash(request, "Only owners can update booking requests.", "danger")
        return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)
    booking_service = BookingService(BookingRepository(db))
    try:
        if action == "confirm":
            booking_service.confirm_booking(booking_id, user.id)
            flash(request, "Booking confirmed.", "success")
        elif action == "reject":
            booking_service.reject_booking(booking_id, user.id)
            flash(request, "Booking rejected.", "success")
        else:
            flash(request, "Unknown booking action", "danger")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(
            url=request.url_for("owner_booking_requests_view"),
            status_code=status.HTTP_303_SEE_OTHER
        )


@router.get("/properties/new", response_class=HTMLResponse, name="property_form_view")
async def property_form_view(request: Request, user: AuthDep):
    if user.role != "owner":
        flash(request, "Only owners can list properties.", "danger")
        return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request=request,
        name="property-form.html",
        context={"user": user},
    )


@router.post("/properties/new", response_class=HTMLResponse, name="property_create_action")
async def property_create_action(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    title: str = Form(...),
    location: str = Form(...),
    property_type: str = Form("studio"),
    description: str = Form(""),
    price: float = Form(...),
):
    if user.role != "owner":
        flash(request, "Only owners can list properties.", "danger")
        return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)
    if user.id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    property_service = PropertyService(PropertyRepository(db))
    try:
        created_property = property_service.create_property(
            owner_id=user.id,
            owner_role=user.role,
            title=title,
            location=location,
            property_type=property_type,
            description=description,
            price=price,
        )
        request.session["published_property_id"] = created_property.id
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)


@router.get("/properties/{property_id}", response_class=HTMLResponse, name="property_detail_view")
async def property_detail_view(
    request: Request,
    property_id: int,
    user: AuthDep,
    db: SessionDep,
):
    property_service = PropertyService(PropertyRepository(db))
    booking_repo = BookingRepository(db)

    property = property_service.get_property(property_id)
    if property is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    student_booking = next(
        (
            booking
            for booking in booking_repo.list_for_student(user.id)
            if booking.property_id == property_id
        ),
        None,
    )
    request_sent_booking = None
    requested_booking_id = request.session.pop("requested_booking_id", None)
    if isinstance(requested_booking_id, int):
        candidate_booking = booking_repo.get_by_id(requested_booking_id)
        if (
            candidate_booking is not None
            and candidate_booking.student_id == user.id
            and candidate_booking.property_id == property_id
        ):
            request_sent_booking = candidate_booking
    bookings_for_owner = booking_repo.list_for_owner(user.id) if user.id == property.owner_id else []

    return templates.TemplateResponse(
        request=request,
        name="property-detail.html",
        context={
            "user": user,
            "property": property,
            "student_booking": student_booking,
            "request_sent_booking": request_sent_booking,
            "bookings_for_owner": bookings_for_owner,
            "is_owner": user.id == property.owner_id,
        },
    )


@router.get("/properties/{property_id}/book", response_class=HTMLResponse, name="property_booking_view")
async def property_booking_view(
    request: Request,
    property_id: int,
    user: AuthDep,
    db: SessionDep,
):
    if user.role == "owner":
        flash(request, "Only students can request a booking.", "danger")
        return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)
    property_service = PropertyService(PropertyRepository(db))
    property = property_service.get_property(property_id)
    if property is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    return templates.TemplateResponse(
        request=request,
        name="property-booking.html",
        context={"user": user, "property": property},
    )


@router.get("/properties/{property_id}/reviews", response_class=HTMLResponse, name="property_reviews_view")
async def property_reviews_view(
    request: Request,
    property_id: int,
    user: AuthDep,
    db: SessionDep,
):
    property_service = PropertyService(PropertyRepository(db))
    property = property_service.get_property(property_id)
    if property is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")
    review_service = ReviewService(ReviewRepository(db))
    return templates.TemplateResponse(
        request=request,
        name="property-reviews.html",
        context={"user": user, "property": property, "reviews": review_service.list_property_reviews(property_id)},
    )


@router.post("/properties/{property_id}/book", response_class=HTMLResponse, name="property_book_action")
async def property_book_action(
    request: Request,
    property_id: int,
    user: AuthDep,
    db: SessionDep,
    check_in: date = Form(...),
    check_out: date = Form(...),
    notes: str = Form(""),
):
    if user.role == "owner":
        flash(request, "Only students can request a booking.", "danger")
        return RedirectResponse(url=request.url_for("user_home_view"), status_code=status.HTTP_303_SEE_OTHER)
    booking_service = BookingService(BookingRepository(db))
    try:
        booking = booking_service.create_booking(
            property_id=property_id,
            student_id=user.id,
            check_in=check_in,
            check_out=check_out,
            notes=notes,
        )
        request.session["requested_booking_id"] = booking.id
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(
        url=request.url_for("property_detail_view", property_id=property_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/properties/{property_id}/bookings/{booking_id}/status", response_class=HTMLResponse, name="booking_status_action")
async def booking_status_action(
    request: Request,
    property_id: int,
    booking_id: int,
    user: AuthDep,
    db: SessionDep,
    action: str = Form(...),
):
    booking_service = BookingService(BookingRepository(db))
    try:
        if action == "confirm":
            booking_service.confirm_booking(booking_id, user.id)
            flash(request, "Booking confirmed.", "success")
        elif action == "reject":
            booking_service.reject_booking(booking_id, user.id)
            flash(request, "Booking rejected.", "success")
        else:
            flash(request, "Unknown booking action", "danger")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(
        url=request.url_for("property_detail_view", property_id=property_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/properties/{property_id}/reviews/{booking_id}", response_class=HTMLResponse, name="review_action")
async def review_action(
    request: Request,
    property_id: int,
    booking_id: int,
    user: AuthDep,
    db: SessionDep,
    rating: int = Form(...),
    comment: str = Form(""),
    reviewer_name: str = Form(...),
    student_id: str = Form(...),
):
    if user.id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    booking_repo = BookingRepository(db)
    booking = booking_repo.get_by_id(booking_id)
    if (
        booking is None
        or booking.student_id != user.id
        or booking.property_id != property_id
        or booking.status == "rejected"
    ):
        flash(request, "Unable to review that booking.", "danger")
        return RedirectResponse(
            url=request.url_for("property_detail_view", property_id=property_id),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    review_service = ReviewService(ReviewRepository(db))
    try:
        review_service.submit_review(
            booking_id=booking_id,
            property_id=property_id,
            reviewer_id=user.id,
            rating=rating,
            comment=comment,
            reviewer_name=reviewer_name,
            student_id=student_id,
        )
        flash(request, "Review submitted successfully.", "success")
    except ValueError as exc:
        flash(request, str(exc), "danger")
    return RedirectResponse(
        url=request.url_for("property_detail_view", property_id=property_id),
        status_code=status.HTTP_303_SEE_OTHER,
    )