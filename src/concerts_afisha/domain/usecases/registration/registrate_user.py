import logging
import re

from concerts_afisha.domain.entities import Roles, User
from concerts_afisha.interfaces.password_hasher import PasswordHasher
from concerts_afisha.interfaces.token_manager import TokenManager
from concerts_afisha.interfaces.user_repository import UserRepository

from . import registration_errors


class RegistrateUserUseCase:
    LOGIN_PATTERN = re.compile(r"^[a-zA-Z0-9._-]{3,32}$")
    PASSWORD_PATTERN = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^a-zA-Z0-9\s]).{8,}$"
    )

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_manager: TokenManager,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_manager = token_manager
        self.logger = logging.getLogger(__name__)

    async def _execute(self, login: str, password: str, roles: list[Roles]) -> User:
        if not self.LOGIN_PATTERN.match(login):
            self.logger.error(f"Registration failed: login {login} is invalid")
            raise registration_errors.InvalidLoginError

        if not self.PASSWORD_PATTERN.match(password):
            self.logger.error("Registration failed: password is too weak")
            raise registration_errors.WeakPasswordError

        if await self._user_repository.get_by_login(login):
            self.logger.error(f"Registration failed: user {login} already exists")
            raise registration_errors.UserAlreadyExistsError

        password_hash = self._password_hasher.hash(password)
        new_user = await self._user_repository.create(login, password_hash, roles)
        token = self._token_manager.create_token(new_user.login)
        new_user.token = token
        self.logger.info(f"User {login} successfully registered")
        return new_user

    async def registrate(self, login: str, password: str) -> User:
        return await self._execute(login, password, roles=[Roles.customer_group_role])

    async def registrate_admin(self, login: str, password: str) -> User:
        return await self._execute(
            login,
            password,
            roles=[
                Roles.admin_group_role,
                Roles.staff_group_role,
                Roles.customer_group_role,
            ],
        )
