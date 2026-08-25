from fastapi import APIRouter, HTTPException, status

from app.models.auth import LoginRequest, LoginResponse
from app.services.auth_service import login_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Login user",
)
async def login(request: LoginRequest) -> LoginResponse:

    result = login_user(
        username=request.username,
        password=request.password,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return LoginResponse(**result)