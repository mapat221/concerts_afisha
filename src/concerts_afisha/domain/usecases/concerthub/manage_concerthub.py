import logging
from datetime import datetime
from decimal import Decimal

from concerts_afisha.domain.entities import (
    AfishaItem,
    ArtistPopularityItem,
    AuditLogItem,
    CustomerTicket,
    GateControlItem,
    Roles,
    SalesMonitoringItem,
    SecretDataItem,
    User,
    VenueConfigItem,
)
from concerts_afisha.implementations.token_manager import token_manager_errors
from concerts_afisha.interfaces.concerthub_repository import ConcertHubRepository
from concerts_afisha.interfaces.token_manager import TokenManager
from concerts_afisha.interfaces.user_repository import UserRepository

from . import concerthub_errors


class ManageConcertHubUseCase:
    def __init__(
        self,
        concerthub_repository: ConcertHubRepository,
        user_repository: UserRepository,
        token_manager: TokenManager,
    ) -> None:
        self._concerthub_repository = concerthub_repository
        self._user_repository = user_repository
        self._token_manager = token_manager
        self.logger = logging.getLogger(__name__)

    async def _get_caller(self, token: str) -> User:
        try:
            caller_login = self._token_manager.get_login_from_token(token)
        except token_manager_errors.InvalidTokenError as exc:
            self.logger.error("Invalid token provided")
            raise concerthub_errors.UnauthorizedError from exc
        caller = await self._user_repository.get_by_login(caller_login)
        if caller is None:
            self.logger.error(f"Caller {caller_login} not found")
            raise concerthub_errors.UnauthorizedError
        return caller

    async def get_afisha(
        self,
        token: str,
        city: str | None,
        genre: str | None,
    ) -> list[AfishaItem]:
        await self._get_caller(token)
        return await self._concerthub_repository.get_afisha(city=city, genre=genre)

    async def get_user_tickets(self, token: str) -> list[CustomerTicket]:
        caller = await self._get_caller(token)
        return await self._concerthub_repository.get_user_tickets(caller.login)

    async def buy_ticket(self, token: str, ticket_id: int) -> CustomerTicket:
        caller = await self._get_caller(token)
        ticket = await self._concerthub_repository.buy_ticket(caller.login, ticket_id)
        if ticket is None:
            self.logger.error(f"Ticket {ticket_id} is not available")
            raise concerthub_errors.NotFoundError
        self.logger.info(f"User {caller.login} bought ticket {ticket_id}")
        return ticket

    async def refund_ticket(self, token: str, ticket_id: int) -> None:
        caller = await self._get_caller(token)
        refunded = await self._concerthub_repository.refund_ticket(
            caller.login, ticket_id
        )
        if not refunded:
            self.logger.error(f"Ticket {ticket_id} not found for refund")
            raise concerthub_errors.NotFoundError
        self.logger.info(f"User {caller.login} refunded ticket {ticket_id}")

    async def get_sales_monitoring(
        self,
        token: str,
        promoter_name: str | None,
        venue_name: str | None,
    ) -> list[SalesMonitoringItem]:
        caller = await self._get_caller(token)
        if (
            Roles.staff_group_role not in caller.roles
            and Roles.admin_group_role not in caller.roles
        ):
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        return await self._concerthub_repository.get_sales_monitoring(
            promoter_name=promoter_name,
            venue_name=venue_name,
        )

    async def get_venues_configuration(self, token: str) -> list[VenueConfigItem]:
        caller = await self._get_caller(token)
        if (
            Roles.staff_group_role not in caller.roles
            and Roles.admin_group_role not in caller.roles
        ):
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        return await self._concerthub_repository.get_venues_configuration()

    async def create_concert(
        self,
        token: str,
        program_name: str,
        start_datetime: datetime,
        age_restriction: str,
        artist_id: int,
        venue_id: int,
        promoter_id: int,
    ) -> int:
        caller = await self._get_caller(token)
        if (
            Roles.staff_group_role not in caller.roles
            and Roles.admin_group_role not in caller.roles
        ):
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        if not program_name.strip():
            raise concerthub_errors.ValidationError
        concert_id = await self._concerthub_repository.create_concert(
            program_name=program_name,
            start_datetime=start_datetime,
            age_restriction=age_restriction,
            artist_id=artist_id,
            venue_id=venue_id,
            promoter_id=promoter_id,
        )
        self.logger.info(f"Staff {caller.login} created concert {concert_id}")
        return concert_id

    async def release_tickets(
        self,
        token: str,
        concert_id: int,
        sector_id: int,
        price: Decimal,
        count: int,
    ) -> list[str]:
        caller = await self._get_caller(token)
        if (
            Roles.staff_group_role not in caller.roles
            and Roles.admin_group_role not in caller.roles
        ):
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        if count <= 0 or price <= 0:
            raise concerthub_errors.ValidationError
        barcodes = await self._concerthub_repository.release_tickets(
            concert_id=concert_id,
            sector_id=sector_id,
            price=price,
            count=count,
        )
        if not barcodes:
            self.logger.error("Sector capacity exceeded or sector not found")
            raise concerthub_errors.ValidationError
        self.logger.info(f"Staff {caller.login} released {count} tickets")
        return barcodes

    async def scan_gate_ticket(self, token: str, barcode: str) -> GateControlItem:
        caller = await self._get_caller(token)
        if (
            Roles.staff_group_role not in caller.roles
            and Roles.admin_group_role not in caller.roles
        ):
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        item = await self._concerthub_repository.scan_gate_ticket(barcode)
        if item is None:
            self.logger.error(f"Barcode {barcode} not found")
            raise concerthub_errors.NotFoundError
        return item

    async def get_artist_popularity(
        self,
        token: str,
        genre: str | None,
    ) -> list[ArtistPopularityItem]:
        caller = await self._get_caller(token)
        if Roles.admin_group_role not in caller.roles:
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        return await self._concerthub_repository.get_artist_popularity(genre=genre)

    async def get_all_tables_list(self, token: str) -> list[str]:
        caller = await self._get_caller(token)
        if Roles.admin_group_role not in caller.roles:
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        return await self._concerthub_repository.get_all_tables_list()

    async def get_table_data(
        self, token: str, table_name: str
    ) -> list[dict[str, str | int | None]]:
        caller = await self._get_caller(token)
        if Roles.admin_group_role not in caller.roles:
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        return await self._concerthub_repository.get_table_data(table_name)

    async def delete_table_record(
        self, token: str, table_name: str, record_id: int
    ) -> None:
        caller = await self._get_caller(token)
        if Roles.admin_group_role not in caller.roles:
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        deleted = await self._concerthub_repository.delete_table_record(
            table_name, record_id
        )
        if not deleted:
            raise concerthub_errors.NotFoundError
        self.logger.info(
            f"Admin {caller.login} deleted record {record_id} from {table_name}"
        )

    async def get_audit_logs(
        self,
        token: str,
        operation_type: str | None,
    ) -> list[AuditLogItem]:
        caller = await self._get_caller(token)
        if Roles.admin_group_role not in caller.roles:
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        return await self._concerthub_repository.get_audit_logs(
            operation_type=operation_type
        )

    async def get_secret_data(self, token: str) -> list[SecretDataItem]:
        caller = await self._get_caller(token)
        if Roles.admin_group_role not in caller.roles:
            self.logger.error(f"Access denied for user {caller.login}")
            raise concerthub_errors.PermissionDeniedError
        return await self._concerthub_repository.get_secret_data()
