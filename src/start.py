import asyncio
import logging
import os

from concerts_afisha.domain.usecases.concerthub import ManageConcertHubUseCase

import environment as env
from api_server.app.app import create_app, start_api_server
from concerts_afisha.domain.entities import Roles
from concerts_afisha.domain.usecases.login import LoginUserUseCase
from concerts_afisha.domain.usecases.registration import (
    RegistrateUserUseCase,
    registration_errors,
)
from concerts_afisha.domain.usecases.roles import ManageRolesUseCase
from concerts_afisha.implementations.concerthub_repository import (
    PostgresConcertHubRepository,
)
from concerts_afisha.implementations.password_hasher import Argon2PasswordHasher
from concerts_afisha.implementations.token_manager import JwtTokenManager
from concerts_afisha.implementations.user_repository import PostgresUserRepository
from utils.config import Configuration

LOGGER = logging.getLogger(__name__)


async def _seed_initial_users(
    registrate_user: RegistrateUserUseCase,
    user_repository: PostgresUserRepository,
    admin_login: str,
    admin_password: str,
) -> None:
    for login in [admin_login, "admin_user"]:
        try:
            await registrate_user.registrate_admin(
                login=login,
                password=admin_password,
            )
        except registration_errors.UserAlreadyExistsError:
            pass

    try:
        await registrate_user.registrate(
            login="ivan_customer",
            password=admin_password,
        )
    except registration_errors.UserAlreadyExistsError:
        pass

    try:
        await registrate_user.registrate(
            login="petrov_staff",
            password=admin_password,
        )
        await user_repository.update_roles(
            login="petrov_staff",
            roles=[Roles.staff_group_role, Roles.customer_group_role],
        )
    except registration_errors.UserAlreadyExistsError:
        pass


def main() -> int:
    try:
        config = Configuration.from_env()
    except Exception:
        LOGGER.critical("Unable to obtain configuration.", exc_info=True)
        return 1

    password_hasher = Argon2PasswordHasher(
        time_cost=config.argon2.time_cost,
        memory_cost=config.argon2.memory_cost,
        parallelism=config.argon2.parallelism,
    )
    token_manager = JwtTokenManager(
        secret_key=config.jwt.secret_key,
    )
    user_repository = PostgresUserRepository(
        url=config.database.url,
    )
    concerthub_repository = PostgresConcertHubRepository(
        url=config.database.url,
    )

    registrate_user = RegistrateUserUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_manager=token_manager,
    )
    login_user = LoginUserUseCase(
        user_repository=user_repository,
        password_hasher=password_hasher,
        token_manager=token_manager,
    )
    manage_roles = ManageRolesUseCase(
        user_repository=user_repository,
        token_manager=token_manager,
    )
    manage_concerthub = ManageConcertHubUseCase(
        concerthub_repository=concerthub_repository,
        user_repository=user_repository,
        token_manager=token_manager,
    )

    try:
        asyncio.run(
            _seed_initial_users(
                registrate_user=registrate_user,
                user_repository=user_repository,
                admin_login=config.admin.login,
                admin_password=config.admin.password,
            )
        )
    except Exception:
        LOGGER.critical("Unable to seed initial users.", exc_info=True)
        return 1

    web_app = create_app(
        registrate_user=registrate_user,
        login_user=login_user,
        manage_roles=manage_roles,
        manage_concerthub=manage_concerthub,
    )

    try:
        start_api_server(web_app, host="0.0.0.0", port=env.SERVE_PORT)
    except Exception:
        LOGGER.critical("API server stopped with error.", exc_info=True)
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    os._exit(exit_code)
