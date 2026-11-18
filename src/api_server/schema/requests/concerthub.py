from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, StrictInt, StrictStr


class BuyTicketRequestBody(BaseModel):
    ticket_id: StrictInt = Field(
        description="Ticket ID to buy",
        examples=[4],
    )


class CreateConcertRequestBody(BaseModel):
    program_name: StrictStr = Field(
        description="Concert program name",
        examples=["Большой концерт Дорочки"],
    )
    start_datetime: datetime = Field(
        description="Concert start date and time",
    )
    age_restriction: StrictStr = Field(
        description="Age restriction",
        examples=["16+"],
    )
    artist_id: StrictInt = Field(
        description="Artist ID",
        examples=[1],
    )
    venue_id: StrictInt = Field(
        description="Venue ID",
        examples=[1],
    )
    promoter_id: StrictInt = Field(
        description="Promoter ID",
        examples=[1],
    )


class ReleaseTicketsRequestBody(BaseModel):
    concert_id: StrictInt = Field(
        description="Concert ID",
        examples=[1],
    )
    sector_id: StrictInt = Field(
        description="Hall sector ID",
        examples=[1],
    )
    price: Decimal = Field(
        description="Ticket price",
        examples=[Decimal(3500)],
    )
    count: StrictInt = Field(
        description="Number of tickets to release",
        examples=[5],
    )


class ScanTicketRequestBody(BaseModel):
    barcode: StrictStr = Field(
        description="Ticket barcode",
        examples=["TK-990101"],
    )
