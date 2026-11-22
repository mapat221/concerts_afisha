from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

# юзерам


# Доступный билет
class AvailableTicketOption(BaseModel):
    ticket_id: int  # id
    barcode: str  # штрихкод
    sector_name: str  # сектор
    price: Decimal  # цена


# один микроэлемент афиши для вью пользователя
class AfishaItem(BaseModel):
    concert_id: int  # id концерта
    artist: str  # артист
    program_name: str  # название концерта
    start_datetime: datetime  # время начала
    age_restriction: str | None = None  # возростное ограничение
    city: str  # город
    venue_name: str  # название площадки
    price_from: Decimal | None = None  # цены от
    available_tickets: list[AvailableTicketOption] = []  # доступные билеты


# билет на концерт
class CustomerTicket(BaseModel):
    ticket_id: int  # id билета
    barcode: str  # штрихкод
    artist: str  # артист
    program_name: str  # название концерта
    start_datetime: datetime  # время начала
    venue_name: str  # название площадки
    sector_name: str  # название сектора площадки
    price: Decimal  # цена
    ticket_status: str  # статус, продан или нет


# персоналу


# вью для организаторов
class SalesMonitoringItem(BaseModel):
    promoter: str  # организатор концерта
    artist: str  # артист
    program_name: str  # название концерта
    venue_name: str  # название площадки
    total_capacity: int  # вместимость площадки проведения
    tickets_sold: int  # число проданных билетов
    occupancy_percent: float  # заполненность зала
    total_revenue: Decimal  # суммарная выручка от проданных билетов


# вью для охраны
class GateControlItem(BaseModel):
    concert_id: int  # id концерта
    start_datetime: datetime  # время начала
    barcode: str  # штрихкод
    ticket_status: str  # статус билета
    sector_name: str  # название сектора
    sector_type: str  # название сектора
    customer_full_name: str | None = None  # фио владельца билета
    phone_number: str | None = None  # телефон владельца билета


# конфигурация площадки
class VenueConfigItem(BaseModel):
    venue_id: int  # id площадки
    venue_name: str  # id сектора
    city: str  # город
    total_capacity: int  # вместимость
    sector_id: int  # id сектора
    sector_name: str  # имя сектора
    sector_capacity: int  # вместимость сектора
    sector_type: str  # тип сектора


# админу


# запись лога
class AuditLogItem(BaseModel):
    log_item_id: int  # id лога
    operation_type: str | None = None  # тип операции
    operation_date: str | None = None  # время операции
    user_operator: str | None = None  # исполнитель операции
    changed_data: str | None = None  # измененная информация


# статистика по артисту
class ArtistPopularityItem(BaseModel):
    artist: str  # артист
    music_genre: str | None = None  # жанр музыки
    total_concerts: int  # проведенные и запланированные концерты
    cities_visited: int  # посещено городов
    total_tickets_sold: int  # всего продано билетов
    total_gross: Decimal  # сборы с исполнителя за все время


# токен
class SecretDataItem(BaseModel):
    id: int  # id токена
    username: str | None = None  # логин пользователя
    secret_token: str | None = None  # токен доступа
