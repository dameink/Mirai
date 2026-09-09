from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from auth.security import hash_password

from auth.models import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
    RefreshTokenRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RegisterResponse,
)

from auth.email_verification import (
    create_verification_code,
    resend_verification_code,
    verify_code,
)

from auth.password_reset import (
    create_reset_code,
    verify_reset_code,
)

from auth.email_service import (
    send_verification_email,
    send_password_reset_email,
)

from auth.service import (
    authenticate_user,
    create_auth_tokens,
    find_user_by_email,
    get_user_from_access_token,
    get_user_from_refresh_token,
    register_user,
    revoke_refresh_token,
    rotate_refresh_token,
    revoke_all_user_sessions,
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
    response_model=RegisterResponse,
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

    verification_code = create_verification_code(
        db,
        user.id,
    )

    send_verification_email(
        user.email,
        verification_code,
    )

    return RegisterResponse(
        message="Registration successful. Please verify your email.",
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

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in.",
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
        "message": "Successfully logged out.",
    }


@router.post("/verify-email")
def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db),
):
    user = find_user_by_email(
        db,
        request.email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code.",
        )

    success = verify_code(
        db,
        user.id,
        request.code,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code.",
        )

    user.email_verified = True

    db.commit()
    db.refresh(user)

    return {
        "message": "Email verified successfully.",
    }


@router.post("/resend-verification")
def resend_verification(
    request: ResendVerificationRequest,
    db: Session = Depends(get_db),
):
    user = find_user_by_email(
        db,
        request.email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to resend verification code.",
        )

    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified.",
        )

    code = resend_verification_code(
        db,
        user.id,
    )

    if code is None:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait 60 seconds before requesting a new code.",
        )

    send_verification_email(
        user.email,
        code,
    )

    return {
        "message": "Verification code sent successfully.",
    }


@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db),
):
    user = find_user_by_email(
        db,
        request.email,
    )

    if user is None:
        return {
            "message": "If the email exists, a password reset code has been sent.",
        }

    if not user.email_verified:
        return {
            "message": "If the email exists, a password reset code has been sent.",
        }

    code = create_reset_code(
        db,
        user.id,
    )

    send_password_reset_email(
        user.email,
        code,
    )

    return {
        "message": "If the email exists, a password reset code has been sent.",
    }


@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db),
):
    user = find_user_by_email(
        db,
        request.email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code.",
        )

    success = verify_reset_code(
        db,
        user.id,
        request.code,
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset code.",
        )

    user.password_hash = hash_password(
        request.new_password,
    )

    revoke_all_user_sessions(
        db,
        user.id,
    )

    db.commit()
    db.refresh(user)

    return {
        "message": "Password reset successfully.",
    }