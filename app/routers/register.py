from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import Request, status, Form
from sqlalchemy.exc import IntegrityError
from app.dependencies import SessionDep
from app.services.auth_service import AuthService
from app.repositories.user import UserRepository
from app.utilities.flash import flash
from . import router, templates

# View route (loads the page)
@router.get("/register", response_class=HTMLResponse)
async def register_view(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="register.html",
    )

# Action route (performs an action)
@router.post('/register', response_class=HTMLResponse, status_code=status.HTTP_201_CREATED)
def signup_user(request:Request, db:SessionDep, 
    username: str = Form(),
    password: str = Form(),
    role: str = Form(),
):
    user_repo = UserRepository(db)
    auth_service = AuthService(user_repo)
    try:
        auth_service.register_user(username, password, role)
        flash(request, "Registration completed! Sign in now!")
        return RedirectResponse(url=request.url_for("login_view"), status_code=status.HTTP_303_SEE_OTHER)
    except ValueError as exc:
        flash(request, str(exc), "danger")
        return RedirectResponse(url=request.url_for("register_view"), status_code=status.HTTP_303_SEE_OTHER)
    except IntegrityError:
        flash(request, "That username is already in use.", "danger")
        return RedirectResponse(url=request.url_for("register_view"), status_code=status.HTTP_303_SEE_OTHER)
