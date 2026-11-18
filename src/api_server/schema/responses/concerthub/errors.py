from typing import Self

from pydantic import BaseModel, Field, StrictStr


class UnauthorizedResponseBody(BaseModel):
    detail: StrictStr = Field(
        description="Error detail",
        examples=["Unauthorized"],
    )

    @classmethod
    def new(cls, detail: str) -> Self:
        return cls(detail=detail)


class PermissionDeniedResponseBody(BaseModel):
    detail: StrictStr = Field(
        description="Error detail",
        examples=["Access denied for caller"],
    )

    @classmethod
    def new(cls, detail: str) -> Self:
        return cls(detail=detail)


class NotFoundResponseBody(BaseModel):
    detail: StrictStr = Field(
        description="Error detail",
        examples=["Resource not found"],
    )

    @classmethod
    def new(cls, detail: str) -> Self:
        return cls(detail=detail)


class ValidationErrorResponseBody(BaseModel):
    detail: StrictStr = Field(
        description="Error detail",
        examples=["Validation error"],
    )

    @classmethod
    def new(cls, detail: str) -> Self:
        return cls(detail=detail)
