from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.database import get_db
from src.infrastructure.auth.repositories import SQLUserRepository
from src.application.use_cases.auth import RegisterUser, LoginUser
from src.application.use_cases.auth.register.dtos import RegisterUserRequestDto, RegisterUserResponseDto
from src.application.use_cases.auth.login.dtos import LoginUserRequestDto, LoginUserResponseDto
from src.domain.errors import ValidationError, UnauthorizedError


from src.application.use_cases.auth.refresh.index import RefreshToken
from src.application.use_cases.auth.refresh.dtos import RefreshTokenRequestDto



router = APIRouter(prefix="/auth", tags=["auth"])


async def get_user_repository(session: AsyncSession = Depends(get_db)) -> SQLUserRepository:
    return SQLUserRepository(session)


@router.post("/register", response_model=RegisterUserResponseDto, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterUserRequestDto,
    session: AsyncSession = Depends(get_db),
    user_repo: SQLUserRepository = Depends(get_user_repository)
):
    use_case = RegisterUser(user_repo)
    try:
        user = await use_case.execute(data)
        await session.commit()
        return user
    except ValidationError as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login", response_model=LoginUserResponseDto)
async def login(
    data: LoginUserRequestDto,
    user_repo: SQLUserRepository = Depends(get_user_repository)
):
    use_case = LoginUser(user_repo)
    try:
        return await use_case.execute(data)
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/refresh", response_model=LoginUserResponseDto)
async def refresh(
    data: RefreshTokenRequestDto,
    user_repo: SQLUserRepository = Depends(get_user_repository)
):
    use_case = RefreshToken(user_repo)
    try:
        return await use_case.execute(data)
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



