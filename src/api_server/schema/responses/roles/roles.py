from typing import Self

from pydantic import BaseModel, Field, StrictStr

from concerts_afisha.domain.entities import Roles


class UserRoleItem(BaseModel):
    login: StrictStr = Field(
        description="User login",
        examples=["Alfredo"],
    )
    roles: list[Roles] = Field(
        description="User roles",
        examples=[[Roles.customer_group_role, Roles.staff_group_role]],
    )


class GetUsersResponseBody(BaseModel):
    users: list[UserRoleItem]

    @classmethod
    def create(cls, users: list[UserRoleItem]) -> Self:
        return cls(users=users)


class SetRolesResponseBody(BaseModel):
    message: StrictStr = Field(
        description="Set roles status",
        examples=["Roles updated"],
    )
    login: StrictStr = Field(
        description="Target user login",
        examples=["Alfredo"],
    )
    roles: list[Roles] = Field(
        description="Target user roles",
        examples=[[Roles.customer_group_role, Roles.staff_group_role]],
    )

    @classmethod
    def create(
        cls,
        message: str,
        login: str,
        roles: list[Roles],
    ) -> Self:
        return cls(
            message=message,
            login=login,
            roles=roles,
        )
