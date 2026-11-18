from pydantic import BaseModel, Field, StrictStr

from concerts_afisha.domain.entities import Roles


class SetRolesRequestBody(BaseModel):
    target_login: StrictStr = Field(
        description="Target user login",
        examples=["Alfredo"],
    )
    roles: list[Roles] = Field(
        description="New roles for target user",
        examples=[[Roles.customer_group_role, Roles.staff_group_role]],
    )
