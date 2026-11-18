from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

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


class ConcertHubRepository(ABC):
    @abstractmethod
    async def get_afisha(
        self,
        city: str | None,
        genre: str | None,
    ) -> list[AfishaItem]:
        pass

    @abstractmethod
    async def get_user_tickets(self, customer_login: str) -> list[CustomerTicket]:
        pass

    @abstractmethod
    async def buy_ticket(
        self, customer_login: str, ticket_id: int
    ) -> CustomerTicket | None:
        pass

    @abstractmethod
    async def refund_ticket(self, customer_login: str, ticket_id: int) -> bool:
        pass

    @abstractmethod
    async def get_sales_monitoring(
        self,
        promoter_name: str | None,
        venue_name: str | None,
    ) -> list[SalesMonitoringItem]:
        pass

    @abstractmethod
    async def get_venues_configuration(self) -> list[VenueConfigItem]:
        pass

    @abstractmethod
    async def create_concert(
        self,
        program_name: str,
        start_datetime: datetime,
        age_restriction: str,
        artist_id: int,
        venue_id: int,
        promoter_id: int,
    ) -> int:
        pass

    @abstractmethod
    async def release_tickets(
        self,
        concert_id: int,
        sector_id: int,
        price: Decimal,
        count: int,
    ) -> list[str]:
        pass

    @abstractmethod
    async def scan_gate_ticket(self, barcode: str) -> GateControlItem | None:
        pass

    @abstractmethod
    async def get_artist_popularity(
        self,
        genre: str | None,
    ) -> list[ArtistPopularityItem]:
        pass

    @abstractmethod
    async def get_all_tables_list(self) -> list[str]:
        pass

    @abstractmethod
    async def get_table_data(
        self, table_name: str
    ) -> list[dict[str, str | int | None]]:
        pass

    @abstractmethod
    async def delete_table_record(self, table_name: str, record_id: int) -> bool:
        pass

    @abstractmethod
    async def get_audit_logs(
        self,
        operation_type: str | None,
    ) -> list[AuditLogItem]:
        pass

    @abstractmethod
    async def get_secret_data(self) -> list[SecretDataItem]:
        pass
