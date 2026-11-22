import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any, ClassVar

from sqlalchemy import Numeric, case, cast, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from concerts_afisha.domain.entities import (
    AfishaItem,
    ArtistOption,
    ArtistPopularityItem,
    AuditLogItem,
    AvailableTicketOption,
    ConcertOption,
    CustomerTicket,
    GateControlItem,
    PromoterOption,
    SalesMonitoringItem,
    SecretDataItem,
    StaffFormOptions,
    VenueConfigItem,
    VenueOption,
)
from concerts_afisha.implementations.db.models import (
    Artist,
    Concert,
    Customer,
    HallSector,
    MainLog,
    Promoter,
    SecretData,
    Ticket,
    TicketOrder,
    Venue,
)
from concerts_afisha.interfaces.concerthub_repository import ConcertHubRepository


class PostgresConcertHubRepository(ConcertHubRepository):
    TABLE_MODELS: ClassVar[dict[str, tuple[Any, Any]]] = {
        "artist": (Artist, Artist.artist_id),
        "promoter": (Promoter, Promoter.promoter_id),
        "venue": (Venue, Venue.venue_id),
        "hall_sector": (HallSector, HallSector.sector_id),
        "customer": (Customer, Customer.customer_id),
        "concert": (Concert, Concert.concert_id),
        "ticket_order": (TicketOrder, TicketOrder.order_id),
        "ticket": (Ticket, Ticket.ticket_id),
        "main_log": (MainLog, MainLog.log_item_id),
        "secret_data": (SecretData, SecretData.ID),
    }

    def __init__(
        self,
        url: str,
    ) -> None:
        self._engine = create_async_engine(url, poolclass=NullPool)
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    def _to_afisha_domain(
        self,
        row: Any,
        available_tickets: list[AvailableTicketOption],
    ) -> AfishaItem:
        return AfishaItem(
            concert_id=int(row.concert_id),
            artist=str(row.stage_name or ""),
            program_name=str(row.program_name or ""),
            start_datetime=row.start_datetime or datetime.now(),
            age_restriction=row.age_restriction,
            city=str(row.city or ""),
            venue_name=str(row.venue_name or ""),
            price_from=row.price_from,
            available_tickets=available_tickets,
        )

    def _to_ticket_domain(self, row: Any) -> CustomerTicket:
        return CustomerTicket(
            ticket_id=int(row.ticket_id),
            barcode=str(row.barcode or ""),
            artist=str(row.stage_name or ""),
            program_name=str(row.program_name or ""),
            start_datetime=row.start_datetime or datetime.now(),
            venue_name=str(row.venue_name or ""),
            sector_name=str(row.sector_name or ""),
            price=row.price or Decimal(0),
            ticket_status=str(row.ticket_status or ""),
        )

    def _to_sales_domain(self, row: Any) -> SalesMonitoringItem:
        return SalesMonitoringItem(
            promoter=str(row.promoter or ""),
            artist=str(row.artist or ""),
            program_name=str(row.program_name or ""),
            venue_name=str(row.venue_name or ""),
            total_capacity=int(row.total_capacity or 0),
            tickets_sold=int(row.tickets_sold or 0),
            occupancy_percent=float(row.occupancy_percent or 0),
            total_revenue=row.total_revenue or Decimal(0),
        )

    def _to_venue_config_domain(self, row: Any) -> VenueConfigItem:
        return VenueConfigItem(
            venue_id=int(row.venue_id),
            venue_name=str(row.venue_name or ""),
            city=str(row.city or ""),
            total_capacity=int(row.total_capacity or 0),
            sector_id=int(row.sector_id),
            sector_name=str(row.sector_name or ""),
            sector_capacity=int(row.sector_capacity or 0),
            sector_type=str(row.sector_type or ""),
        )

    def _to_gate_domain(self, row: Any) -> GateControlItem:
        return GateControlItem(
            concert_id=int(row.concert_id),
            start_datetime=row.start_datetime or datetime.now(),
            barcode=str(row.barcode or ""),
            ticket_status=str(row.ticket_status or ""),
            sector_name=str(row.sector_name or ""),
            sector_type=str(row.sector_type or ""),
            customer_full_name=row.customer_full_name,
            phone_number=row.phone_number,
        )

    def _to_popularity_domain(self, row: Any) -> ArtistPopularityItem:
        return ArtistPopularityItem(
            artist=str(row.artist or ""),
            music_genre=row.music_genre,
            total_concerts=int(row.total_concerts or 0),
            cities_visited=int(row.cities_visited or 0),
            total_tickets_sold=int(row.total_tickets_sold or 0),
            total_gross=row.total_gross or Decimal(0),
        )

    def _to_audit_log_domain(self, log_orm: MainLog) -> AuditLogItem:
        return AuditLogItem(
            log_item_id=log_orm.log_item_id,
            operation_type=log_orm.operation_type,
            operation_date=log_orm.operation_date,
            user_operator=log_orm.user_operator,
            changed_data=log_orm.changed_data,
        )

    def _to_secret_data_domain(self, secret_orm: SecretData) -> SecretDataItem:
        return SecretDataItem(
            id=secret_orm.ID,
            username=secret_orm.username,
            secret_token=secret_orm.secret_token,
        )

    async def get_afisha(
        self,
        city: str | None,
        genre: str | None,
    ) -> list[AfishaItem]:
        async with self._session_factory() as session:
            request = (
                select(
                    Concert.concert_id,
                    Artist.stage_name,
                    Concert.program_name,
                    Concert.start_datetime,
                    Concert.age_restriction,
                    Venue.city,
                    Venue.venue_name,
                    func.min(
                        case(
                            (Ticket.ticket_status == "Доступен", Ticket.price),
                            else_=None,
                        )
                    ).label("price_from"),
                )
                .join(Artist, Concert.artist_id == Artist.artist_id)
                .join(Venue, Concert.venue_id == Venue.venue_id)
                .outerjoin(Ticket, Concert.concert_id == Ticket.concert_id)
                .group_by(
                    Concert.concert_id,
                    Artist.stage_name,
                    Concert.program_name,
                    Concert.start_datetime,
                    Concert.age_restriction,
                    Venue.city,
                    Venue.venue_name,
                )
                .order_by(Concert.start_datetime)
            )
            if city:
                request = request.where(Venue.city.ilike(f"%{city}%"))
            if genre:
                request = request.where(Artist.music_genre.ilike(f"%{genre}%"))

            rows = (await session.execute(request)).all()

            tickets_request = (
                select(
                    Ticket.ticket_id,
                    Ticket.concert_id,
                    Ticket.barcode,
                    Ticket.price,
                    HallSector.sector_name,
                )
                .join(HallSector, Ticket.sector_id == HallSector.sector_id)
                .where(Ticket.ticket_status == "Доступен")
                .order_by(Ticket.price, Ticket.ticket_id)
            )
            ticket_rows = (await session.execute(tickets_request)).all()

            tickets_by_concert: dict[int, list[AvailableTicketOption]] = {}
            for t_row in ticket_rows:
                c_id = int(t_row.concert_id)
                if c_id not in tickets_by_concert:
                    tickets_by_concert[c_id] = []
                tickets_by_concert[c_id].append(
                    AvailableTicketOption(
                        ticket_id=int(t_row.ticket_id),
                        barcode=str(t_row.barcode or ""),
                        sector_name=str(t_row.sector_name or ""),
                        price=t_row.price or Decimal(0),
                    )
                )

            return [
                self._to_afisha_domain(
                    row,
                    tickets_by_concert.get(int(row.concert_id), []),
                )
                for row in rows
            ]

    async def get_user_tickets(self, customer_login: str) -> list[CustomerTicket]:
        async with self._session_factory() as session:
            request = (
                select(
                    Ticket.ticket_id,
                    Ticket.barcode,
                    Artist.stage_name,
                    Concert.program_name,
                    Concert.start_datetime,
                    Venue.venue_name,
                    HallSector.sector_name,
                    Ticket.price,
                    Ticket.ticket_status,
                )
                .join(TicketOrder, Ticket.order_id == TicketOrder.order_id)
                .join(Customer, TicketOrder.customer_id == Customer.customer_id)
                .join(Concert, Ticket.concert_id == Concert.concert_id)
                .join(Artist, Concert.artist_id == Artist.artist_id)
                .join(Venue, Concert.venue_id == Venue.venue_id)
                .join(HallSector, Ticket.sector_id == HallSector.sector_id)
                .where(
                    (Customer.email == customer_login)
                    | (Customer.customer_full_name == customer_login)
                )
                .order_by(Concert.start_datetime)
            )
            rows = (await session.execute(request)).all()
            return [self._to_ticket_domain(row) for row in rows]

    async def buy_ticket(
        self, customer_login: str, ticket_id: int
    ) -> CustomerTicket | None:
        async with self._session_factory() as session:
            ticket_request = select(Ticket).where(
                Ticket.ticket_id == ticket_id,
                Ticket.ticket_status == "Доступен",
            )
            ticket_orm = await session.scalar(ticket_request)
            if ticket_orm is None:
                return None

            customer_request = select(Customer).where(
                (Customer.email == customer_login)
                | (Customer.customer_full_name == customer_login)
            )
            customer_orm = await session.scalar(customer_request)
            if customer_orm is None:
                customer_orm = Customer(
                    customer_full_name=customer_login,
                    email=customer_login,
                )
                session.add(customer_orm)
                await session.flush()

            order_orm = TicketOrder(
                order_datetime=datetime.now(),
                order_status="Оплачен",
                total_amount=ticket_orm.price or Decimal(0),
                customer_id=customer_orm.customer_id,
            )
            session.add(order_orm)
            await session.flush()

            ticket_orm.order_id = order_orm.order_id
            ticket_orm.ticket_status = "Продан"
            await session.commit()

            info_request = (
                select(
                    Ticket.ticket_id,
                    Ticket.barcode,
                    Artist.stage_name,
                    Concert.program_name,
                    Concert.start_datetime,
                    Venue.venue_name,
                    HallSector.sector_name,
                    Ticket.price,
                    Ticket.ticket_status,
                )
                .join(Concert, Ticket.concert_id == Concert.concert_id)
                .join(Artist, Concert.artist_id == Artist.artist_id)
                .join(Venue, Concert.venue_id == Venue.venue_id)
                .join(HallSector, Ticket.sector_id == HallSector.sector_id)
                .where(Ticket.ticket_id == ticket_id)
            )
            row = (await session.execute(info_request)).first()
            if row is None:
                return None
            return self._to_ticket_domain(row)

    async def refund_ticket(self, customer_login: str, ticket_id: int) -> bool:
        async with self._session_factory() as session:
            request = (
                select(Ticket, TicketOrder)
                .join(TicketOrder, Ticket.order_id == TicketOrder.order_id)
                .join(Customer, TicketOrder.customer_id == Customer.customer_id)
                .where(
                    Ticket.ticket_id == ticket_id,
                    (Customer.email == customer_login)
                    | (Customer.customer_full_name == customer_login),
                )
            )
            row = (await session.execute(request)).first()
            if row is None:
                return False

            ticket_orm, order_orm = row
            ticket_orm.ticket_status = "Доступен"
            ticket_orm.order_id = None
            order_orm.order_status = "Возврат"
            order_orm.total_amount = Decimal(0)
            await session.commit()
            return True

    async def get_sales_monitoring(
        self,
        promoter_name: str | None,
        venue_name: str | None,
    ) -> list[SalesMonitoringItem]:
        async with self._session_factory() as session:
            sold_count = func.count(
                case((Ticket.ticket_status == "Продан", 1), else_=None)
            )
            total_rev = func.coalesce(
                func.sum(
                    case(
                        (Ticket.ticket_status == "Продан", Ticket.price),
                        else_=Decimal(0),
                    )
                ),
                Decimal(0),
            )
            occupancy = func.round(
                (cast(sold_count, Numeric) / cast(Venue.total_capacity, Numeric)) * 100,
                2,
            )

            request = (
                select(
                    Promoter.company_name.label("promoter"),
                    Artist.stage_name.label("artist"),
                    Concert.program_name,
                    Venue.venue_name,
                    Venue.total_capacity,
                    sold_count.label("tickets_sold"),
                    occupancy.label("occupancy_percent"),
                    total_rev.label("total_revenue"),
                )
                .join(Concert, Promoter.promoter_id == Concert.promoter_id)
                .join(Artist, Concert.artist_id == Artist.artist_id)
                .join(Venue, Concert.venue_id == Venue.venue_id)
                .outerjoin(Ticket, Concert.concert_id == Ticket.concert_id)
                .group_by(
                    Promoter.company_name,
                    Artist.stage_name,
                    Concert.program_name,
                    Venue.venue_name,
                    Venue.total_capacity,
                )
                .order_by(total_rev.desc())
            )
            if promoter_name:
                request = request.where(
                    Promoter.company_name.ilike(f"%{promoter_name}%")
                )
            if venue_name:
                request = request.where(Venue.venue_name.ilike(f"%{venue_name}%"))

            rows = (await session.execute(request)).all()
            return [self._to_sales_domain(row) for row in rows]

    async def get_venues_configuration(self) -> list[VenueConfigItem]:
        async with self._session_factory() as session:
            request = (
                select(
                    Venue.venue_id,
                    Venue.venue_name,
                    Venue.city,
                    Venue.total_capacity,
                    HallSector.sector_id,
                    HallSector.sector_name,
                    HallSector.sector_capacity,
                    HallSector.sector_type,
                )
                .join(HallSector, Venue.venue_id == HallSector.venue_id)
                .order_by(Venue.venue_id, HallSector.sector_id)
            )
            rows = (await session.execute(request)).all()
            return [self._to_venue_config_domain(row) for row in rows]

    async def get_staff_form_options(self) -> StaffFormOptions:
        async with self._session_factory() as session:
            artist_orms: Any = (
                await session.scalars(select(Artist).order_by(Artist.artist_id))
            ).all()
            venue_orms: Any = (
                await session.scalars(select(Venue).order_by(Venue.venue_id))
            ).all()
            promoter_orms: Any = (
                await session.scalars(select(Promoter).order_by(Promoter.promoter_id))
            ).all()

            concerts_request = (
                select(
                    Concert.concert_id,
                    Concert.program_name,
                    Artist.stage_name,
                    Venue.venue_id,
                    Venue.venue_name,
                )
                .join(Artist, Concert.artist_id == Artist.artist_id)
                .join(Venue, Concert.venue_id == Venue.venue_id)
                .order_by(Concert.concert_id)
            )
            concert_rows = (await session.execute(concerts_request)).all()

            sectors_request = (
                select(
                    Venue.venue_id,
                    Venue.venue_name,
                    Venue.city,
                    Venue.total_capacity,
                    HallSector.sector_id,
                    HallSector.sector_name,
                    HallSector.sector_capacity,
                    HallSector.sector_type,
                )
                .join(HallSector, Venue.venue_id == HallSector.venue_id)
                .order_by(Venue.venue_id, HallSector.sector_id)
            )
            sector_rows = (await session.execute(sectors_request)).all()

            barcodes_request = select(Ticket.barcode).order_by(Ticket.ticket_id)
            barcode_vals: Any = (await session.scalars(barcodes_request)).all()

            return StaffFormOptions(
                artists=[
                    ArtistOption(
                        artist_id=int(a.artist_id),
                        stage_name=str(a.stage_name or ""),
                        music_genre=str(a.music_genre or ""),
                    )
                    for a in artist_orms
                ],
                venues=[
                    VenueOption(
                        venue_id=int(v.venue_id),
                        venue_name=str(v.venue_name or ""),
                        city=str(v.city or ""),
                    )
                    for v in venue_orms
                ],
                promoters=[
                    PromoterOption(
                        promoter_id=int(p.promoter_id),
                        company_name=str(p.company_name or ""),
                    )
                    for p in promoter_orms
                ],
                concerts=[
                    ConcertOption(
                        concert_id=int(c.concert_id),
                        program_name=str(c.program_name or ""),
                        artist_name=str(c.stage_name or ""),
                        venue_id=int(c.venue_id),
                        venue_name=str(c.venue_name or ""),
                    )
                    for c in concert_rows
                ],
                sectors=[self._to_venue_config_domain(s) for s in sector_rows],
                barcodes=[str(b) for b in barcode_vals if b],
            )

    async def create_concert(
        self,
        program_name: str,
        start_datetime: datetime,
        age_restriction: str,
        artist_id: int,
        venue_id: int,
        promoter_id: int,
    ) -> int:
        async with self._session_factory() as session:
            concert_orm = Concert(
                program_name=program_name,
                start_datetime=start_datetime,
                age_restriction=age_restriction,
                artist_id=artist_id,
                venue_id=venue_id,
                promoter_id=promoter_id,
            )
            session.add(concert_orm)
            await session.commit()
            return concert_orm.concert_id

    async def release_tickets(
        self,
        concert_id: int,
        sector_id: int,
        price: Decimal,
        count: int,
    ) -> list[str]:
        async with self._session_factory() as session:
            sector_request = select(HallSector).where(HallSector.sector_id == sector_id)
            sector_orm = await session.scalar(sector_request)
            if sector_orm is None:
                return []

            count_request = select(func.count(Ticket.ticket_id)).where(
                Ticket.concert_id == concert_id,
                Ticket.sector_id == sector_id,
            )
            existing_count = await session.scalar(count_request)
            current = int(existing_count or 0)
            if (
                sector_orm.sector_capacity is not None
                and current + count > sector_orm.sector_capacity
            ):
                return []

            barcodes: list[str] = []
            for _ in range(count):
                code = f"TK-{concert_id}{sector_id}-{uuid.uuid4().hex[:6].upper()}"
                barcodes.append(code)
                ticket_orm = Ticket(
                    barcode=code,
                    price=price,
                    ticket_status="Доступен",
                    concert_id=concert_id,
                    sector_id=sector_id,
                    order_id=None,
                )
                session.add(ticket_orm)
            await session.commit()
            return barcodes

    async def scan_gate_ticket(self, barcode: str) -> GateControlItem | None:
        async with self._session_factory() as session:
            request = (
                select(
                    Concert.concert_id,
                    Concert.start_datetime,
                    Ticket.barcode,
                    Ticket.ticket_status,
                    HallSector.sector_name,
                    HallSector.sector_type,
                    Customer.customer_full_name,
                    Customer.phone_number,
                )
                .join(Concert, Ticket.concert_id == Concert.concert_id)
                .join(HallSector, Ticket.sector_id == HallSector.sector_id)
                .outerjoin(TicketOrder, Ticket.order_id == TicketOrder.order_id)
                .outerjoin(Customer, TicketOrder.customer_id == Customer.customer_id)
                .where(Ticket.barcode == barcode)
            )
            row = (await session.execute(request)).first()
            if row is None:
                return None
            return self._to_gate_domain(row)

    async def get_artist_popularity(
        self,
        genre: str | None,
    ) -> list[ArtistPopularityItem]:
        async with self._session_factory() as session:
            sold_tickets = func.sum(
                case((Ticket.ticket_status == "Продан", 1), else_=0)
            )
            total_gross = func.coalesce(
                func.sum(
                    case(
                        (Ticket.ticket_status == "Продан", Ticket.price),
                        else_=Decimal(0),
                    )
                ),
                Decimal(0),
            )

            request = (
                select(
                    Artist.stage_name.label("artist"),
                    Artist.music_genre,
                    func.count(func.distinct(Concert.concert_id)).label(
                        "total_concerts"
                    ),
                    func.count(func.distinct(Venue.city)).label("cities_visited"),
                    sold_tickets.label("total_tickets_sold"),
                    total_gross.label("total_gross"),
                )
                .join(Concert, Artist.artist_id == Concert.artist_id)
                .join(Venue, Concert.venue_id == Venue.venue_id)
                .outerjoin(Ticket, Concert.concert_id == Ticket.concert_id)
                .group_by(Artist.stage_name, Artist.music_genre)
                .order_by(total_gross.desc())
            )
            if genre:
                request = request.where(Artist.music_genre.ilike(f"%{genre}%"))

            rows = (await session.execute(request)).all()
            return [self._to_popularity_domain(row) for row in rows]

    async def get_all_tables_list(self) -> list[str]:
        return list(self.TABLE_MODELS.keys())

    async def get_table_data(
        self, table_name: str
    ) -> list[dict[str, str | int | None]]:
        if table_name not in self.TABLE_MODELS:
            return []
        model, pk_col = self.TABLE_MODELS[table_name]
        async with self._session_factory() as session:
            request = select(model).order_by(pk_col)
            orms: Any = (await session.scalars(request)).all()
            result: list[dict[str, str | int | None]] = []
            for orm_obj in orms:
                row_dict: dict[str, str | int | None] = {}
                for col in model.__table__.columns:
                    val = getattr(orm_obj, col.key)
                    if isinstance(val, (datetime, date, Decimal)):
                        row_dict[col.key] = str(val)
                    else:
                        row_dict[col.key] = val
                result.append(row_dict)
            return result

    async def delete_table_record(self, table_name: str, record_id: int) -> bool:
        if table_name not in self.TABLE_MODELS:
            return False
        model, pk_col = self.TABLE_MODELS[table_name]
        async with self._session_factory() as session:
            request = select(model).where(pk_col == record_id)
            orm_obj = await session.scalar(request)
            if orm_obj is None:
                return False
            await session.delete(orm_obj)
            await session.commit()
            return True

    async def get_audit_logs(
        self,
        operation_type: str | None,
    ) -> list[AuditLogItem]:
        async with self._session_factory() as session:
            request = select(MainLog).order_by(MainLog.log_item_id.desc())
            if operation_type:
                request = request.where(MainLog.operation_type == operation_type)
            log_orms: Any = (await session.scalars(request)).all()
            return [self._to_audit_log_domain(log) for log in log_orms]

    async def get_secret_data(self) -> list[SecretDataItem]:
        async with self._session_factory() as session:
            request = select(SecretData).order_by(SecretData.ID)
            secret_orms: Any = (await session.scalars(request)).all()
            return [self._to_secret_data_domain(item) for item in secret_orms]
