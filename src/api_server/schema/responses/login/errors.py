from typing import Self

from pydantic import BaseModel, Field, StrictStr


class UserNotFoundResponseBody(BaseModel):
    detail: StrictStr = Field(
        description="Error detail",
        examples=["User not found"],
    )

    @classmethod
    def new(cls, detail: str) -> Self:
        return cls(detail=detail)


class InvalidPasswordResponseBody(BaseModel):
    detail: StrictStr = Field(
        description="Error detail",
        examples=["Invalid password for user"],
    )

    @classmethod
    def new(cls, detail: str) -> Self:
        return cls(detail=detail)
