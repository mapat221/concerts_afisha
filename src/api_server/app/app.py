import uvicorn
from concerts_afisha.domain.usecases.concerthub import ManageConcertHubUseCase
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_server.app import dependency
from api_server.routes import (
    concerthub_router,
    login_router,
    registration_router,
    roles_router,
)
from concerts_afisha.domain.usecases.login import LoginUserUseCase
from concerts_afisha.domain.usecases.registration import RegistrateUserUseCase
from concerts_afisha.domain.usecases.roles import ManageRolesUseCase


def create_app(
    registrate_user: RegistrateUserUseCase,
    login_user: LoginUserUseCase,
    manage_roles: ManageRolesUseCase,
    manage_concerthub: ManageConcertHubUseCase,
) -> FastAPI:
    dependency.registrate_user = registrate_user
    dependency.login_user = login_user
    dependency.manage_roles = manage_roles
    dependency.manage_concerthub = manage_concerthub

    web_app = FastAPI(title="ConcertHub")
    web_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    web_app.include_router(registration_router)
    web_app.include_router(login_router)
    web_app.include_router(roles_router)
    web_app.include_router(concerthub_router)
    return web_app


def start_api_server(web_app: FastAPI, host: str, port: int) -> None:
    uvicorn.run(web_app, host=host, port=port)
