from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from auth.models import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
    RefreshTokenRequest,
)

from auth.service import (
    authenticate_user,
    create_auth_tokens,
    get_user_from_access_token,
    get_user_from_refresh_token,
    register_user,
    revoke_refresh_token,
    rotate_refresh_token,
)

from db.database import get_db


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

security = HTTPBearer()


def _user_response(user):
    return UserResponse(
        id=user["id"],
        email=user["email"],
        created_at=user["created_at"].isoformat(),
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    user = get_user_from_access_token(
        db,
        token,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token.",
        )

    return user


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = register_user(
            db,
            email=request.email,
            password=request.password,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    access_token, refresh_token = create_auth_tokens(
        db,
        user.id,
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        email=request.email,
        password=request.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    access_token, refresh_token = create_auth_tokens(
        db,
        user.id,
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def me(
    user=Depends(get_current_user),
):
    return _user_response(user)


@router.post(
    "/refresh",
    response_model=AuthResponse,
)
def refresh(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    result = rotate_refresh_token(
        db,
        request.refresh_token,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked refresh token.",
        )

    access_token, new_refresh_token = result

    user = get_user_from_refresh_token(
        db,
        new_refresh_token,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return AuthResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.post("/logout")
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    revoke_refresh_token(
        db,
        request.refresh_token,
    )

    return {
        "message": "Successfully logged out."
    }