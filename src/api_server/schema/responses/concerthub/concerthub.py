from typing import Self

from pydantic import BaseModel, Field, StrictInt, StrictStr

from concerts_afisha.domain.entities import (
    AfishaItem,
    ArtistPopularityItem,
    AuditLogItem,
    CustomerTicket,
    GateControlItem,
    SalesMonitoringItem,
    SecretDataItem,
    VenueConfigItem,
)


class GetAfishaResponseBody(BaseModel):
    items: list[AfishaItem]

    @classmethod
    def create(cls, items: list[AfishaItem]) -> Self:
        return cls(items=items)


class GetUserTicketsResponseBody(BaseModel):
    tickets: list[CustomerTicket]

    @classmethod
    def create(cls, tickets: list[CustomerTicket]) -> Self:
        return cls(tickets=tickets)


class BuyTicketResponseBody(BaseModel):
    ticket: CustomerTicket

    @classmethod
    def create(cls, ticket: CustomerTicket) -> Self:
        return cls(ticket=ticket)


class ActionMessageResponseBody(BaseModel):
    message: StrictStr = Field(
        description="Action status",
        examples=["Operation completed"],
    )

    @classmethod
    def create(cls, message: str) -> Self:
        return cls(message=message)


class GetSalesMonitoringResponseBody(BaseModel):
    items: list[SalesMonitoringItem]

    @classmethod
    def create(cls, items: list[SalesMonitoringItem]) -> Self:
        return cls(items=items)


class GetVenuesConfigResponseBody(BaseModel):
    items: list[VenueConfigItem]

    @classmethod
    def create(cls, items: list[VenueConfigItem]) -> Self:
        return cls(items=items)


class CreateConcertResponseBody(BaseModel):
    concert_id: StrictInt

    @classmethod
    def create(cls, concert_id: int) -> Self:
        return cls(concert_id=concert_id)


class ReleaseTicketsResponseBody(BaseModel):
    barcodes: list[StrictStr]

    @classmethod
    def create(cls, barcodes: list[str]) -> Self:
        return cls(barcodes=barcodes)


class ScanGateTicketResponseBody(BaseModel):
    item: GateControlItem

    @classmethod
    def create(cls, item: GateControlItem) -> Self:
        return cls(item=item)


class GetArtistPopularityResponseBody(BaseModel):
    items: list[ArtistPopularityItem]

    @classmethod
    def create(cls, items: list[ArtistPopularityItem]) -> Self:
        return cls(items=items)


class GetAllTablesResponseBody(BaseModel):
    tables: list[StrictStr]

    @classmethod
    def create(cls, tables: list[str]) -> Self:
        return cls(tables=tables)


class GetTableDataResponseBody(BaseModel):
    rows: list[dict[str, str | int | None]]

    @classmethod
    def create(cls, rows: list[dict[str, str | int | None]]) -> Self:
        return cls(rows=rows)


class GetAuditLogsResponseBody(BaseModel):
    logs: list[AuditLogItem]

    @classmethod
    def create(cls, logs: list[AuditLogItem]) -> Self:
        return cls(logs=logs)


class GetSecretDataResponseBody(BaseModel):
    items: list[SecretDataItem]

    @classmethod
    def create(cls, items: list[SecretDataItem]) -> Self:
        return cls(items=items)
