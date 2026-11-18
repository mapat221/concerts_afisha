from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRoleOrm(Base):
    __tablename__ = "user_roles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    )


class UserOrm(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    roles: Mapped[list["RoleOrm"]] = relationship(
        secondary="user_roles",
        lazy="selectin",
    )


class RoleOrm(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class Artist(Base):
    __tablename__ = "artist"

    artist_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    stage_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    leader_full_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    music_genre: Mapped[str | None] = mapped_column(Text, nullable=True)


class Promoter(Base):
    __tablename__ = "promoter"

    promoter_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    company_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_person: Mapped[str | None] = mapped_column(Text, nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(Text, nullable=True)


class Venue(Base):
    __tablename__ = "venue"

    venue_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    venue_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)


class HallSector(Base):
    __tablename__ = "hall_sector"

    sector_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    sector_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    sector_capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sector_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    venue_id: Mapped[int] = mapped_column(
        ForeignKey("venue.venue_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )


class Customer(Base):
    __tablename__ = "customer"

    customer_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    customer_full_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (Index("idx_customer_email", "email"),)


class TicketOrder(Base):
    __tablename__ = "ticket_order"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    order_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customer.customer_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (Index("idx_order_status", "order_status"),)


class Concert(Base):
    __tablename__ = "concert"

    concert_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    program_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    age_restriction: Mapped[str | None] = mapped_column(Text, nullable=True)
    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artist.artist_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    venue_id: Mapped[int] = mapped_column(
        ForeignKey("venue.venue_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    promoter_id: Mapped[int] = mapped_column(
        ForeignKey("promoter.promoter_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        Index("idx_concert_datetime", "start_datetime"),
        Index("idx_concert_artist_datetime", "artist_id", "start_datetime"),
    )


class Ticket(Base):
    __tablename__ = "ticket"

    ticket_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    barcode: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    ticket_status: Mapped[str | None] = mapped_column(Text, nullable=True)
    concert_id: Mapped[int] = mapped_column(
        ForeignKey("concert.concert_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    sector_id: Mapped[int] = mapped_column(
        ForeignKey("hall_sector.sector_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("ticket_order.order_id", onupdate="CASCADE", ondelete="SET NULL"),
        nullable=True,
    )

    __table_args__ = (
        Index("idx_ticket_status", "ticket_status"),
        Index("idx_ticket_concert", "concert_id"),
    )


class MainLog(Base):
    __tablename__ = "main_log"

    log_item_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    operation_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    operation_date: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_operator: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_data: Mapped[str | None] = mapped_column(Text, nullable=True)


class SecretData(Base):
    __tablename__ = "secret_data"

    ID: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str | None] = mapped_column(Text, nullable=True)
    secret_token: Mapped[str | None] = mapped_column(Text, nullable=True)
