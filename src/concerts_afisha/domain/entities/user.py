from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class Roles(StrEnum):
    customer_group_role = "customer_group_role"
    staff_group_role = "staff_group_role"
    admin_group_role = "admin_group_role"


class User(BaseModel):
    id_: str
    login: str
    created_at: datetime
    password_hash: str
    roles: list[Roles]
    token: str = ""
