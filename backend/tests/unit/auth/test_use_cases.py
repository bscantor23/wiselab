import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.application.use_cases.auth import RegisterUser, LoginUser
from src.application.use_cases.auth.register.dtos import RegisterUserRequestDto
from src.application.use_cases.auth.login.dtos import LoginUserRequestDto
from src.domain.errors import ValidationError, UnauthorizedError
from src.domain.auth.models import User
from src.domain.auth.value_objects import Email
import uuid

@pytest.mark.asyncio
async def test_register_user_success():
    mock_repo = MagicMock()
    mock_repo.get_by_email = AsyncMock(return_value=None)
    mock_repo.add = AsyncMock()

    use_case = RegisterUser(mock_repo)
    data = RegisterUserRequestDto(
        email="test@example.com",
        password="Password123!",
        full_name="Test User"
    )
    result = await use_case.execute(data)

    assert result.email == "test@example.com"
    assert result.full_name == "Test User"
    mock_repo.add.assert_called_once()

@pytest.mark.asyncio
async def test_register_user_already_exists():
    mock_repo = MagicMock()
    existing_user = MagicMock()
    mock_repo.get_by_email = AsyncMock(return_value=existing_user)

    use_case = RegisterUser(mock_repo)
    data = RegisterUserRequestDto(email="existing@example.com", password="Password123!")

    with pytest.raises(ValidationError, match="Email already registered"):
        await use_case.execute(data)

@pytest.mark.asyncio
async def test_login_user_success():
    from src.infrastructure.auth.services.hasher import Hasher
    
    password = "Password123!"
    hashed = Hasher.get_password_hash(password)
    
    mock_user = MagicMock(spec=User)
    mock_user.id = uuid.uuid4()
    mock_user.email = Email("test@example.com")
    mock_user.password_hash = hashed
    mock_user.is_active = True
    mock_user.full_name = "Test User"

    mock_repo = MagicMock()
    mock_repo.get_by_email = AsyncMock(return_value=mock_user)

    use_case = LoginUser(mock_repo)
    data = LoginUserRequestDto(email="test@example.com", password=password)

    result = await use_case.execute(data)

    assert result.access_token is not None
    assert result.refresh_token is not None
    assert result.token_type == "bearer"

@pytest.mark.asyncio
async def test_login_user_inactive():
    mock_user = MagicMock(spec=User)
    mock_user.password_hash = "hash"
    mock_user.is_active = False
    mock_user.full_name = "Inactive User"

    with patch("src.infrastructure.auth.services.hasher.Hasher.verify_password", return_value=True):
        mock_repo = MagicMock()
        mock_repo.get_by_email = AsyncMock(return_value=mock_user)
        use_case = LoginUser(mock_repo)
        data = LoginUserRequestDto(email="test@example.com", password="Password123!")
        
        with pytest.raises(UnauthorizedError, match="User account is deactivated"):
            await use_case.execute(data)

@pytest.mark.asyncio
async def test_login_user_invalid_password():
    mock_user = MagicMock(spec=User)
    mock_user.password_hash = "different-hash"
    mock_user.is_active = True
    mock_user.full_name = "Invalid Pass"

    mock_repo = MagicMock()
    mock_repo.get_by_email = AsyncMock(return_value=mock_user)

    use_case = LoginUser(mock_repo)
    data = LoginUserRequestDto(email="test@example.com", password="Password123!")

    with pytest.raises(UnauthorizedError, match="Invalid credentials"):
        await use_case.execute(data)
