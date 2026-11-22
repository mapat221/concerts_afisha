from typing import Annotated

from fastapi import APIRouter, Header, status
from fastapi.responses import JSONResponse

from api_server import schema
from api_server.app import dependency
from concerts_afisha.domain.usecases.concerthub import concerthub_errors

concerthub_router = APIRouter(
    prefix="/api",
    tags=["concerthub"],
)


@concerthub_router.get(
    "/afisha",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.GetAfishaResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
    },
)
async def get_afisha(
    token: Annotated[str, Header()],
    city: str | None = None,
    genre: str | None = None,
) -> schema.responses.concerthub.GetAfishaResponseBody | JSONResponse:
    try:
        items = await dependency.manage_concerthub.get_afisha(
            token=token,
            city=city,
            genre=genre,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    return schema.responses.concerthub.GetAfishaResponseBody.create(items=items)


@concerthub_router.get(
    "/tickets/user",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.GetUserTicketsResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
    },
)
async def get_user_tickets(
    token: Annotated[str, Header()],
) -> schema.responses.concerthub.GetUserTicketsResponseBody | JSONResponse:
    try:
        tickets = await dependency.manage_concerthub.get_user_tickets(token=token)
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    return schema.responses.concerthub.GetUserTicketsResponseBody.create(
        tickets=tickets
    )


@concerthub_router.post(
    "/tickets/buy",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.BuyTicketResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schema.responses.concerthub.errors.NotFoundResponseBody
        },
    },
)
async def buy_ticket(
    token: Annotated[str, Header()],
    body: schema.requests.concerthub.BuyTicketRequestBody,
) -> schema.responses.concerthub.BuyTicketResponseBody | JSONResponse:
    try:
        ticket = await dependency.manage_concerthub.buy_ticket(
            token=token,
            ticket_id=body.ticket_id,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.NotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=schema.responses.concerthub.errors.NotFoundResponseBody.new(
                detail="Ticket not found or already sold"
            ).model_dump(),
        )
    return schema.responses.concerthub.BuyTicketResponseBody.create(ticket=ticket)


@concerthub_router.post(
    "/tickets/{ticket_id}/refund",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.ActionMessageResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schema.responses.concerthub.errors.NotFoundResponseBody
        },
    },
)
async def refund_ticket(
    token: Annotated[str, Header()],
    ticket_id: int,
) -> schema.responses.concerthub.ActionMessageResponseBody | JSONResponse:
    try:
        await dependency.manage_concerthub.refund_ticket(
            token=token,
            ticket_id=ticket_id,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.NotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=schema.responses.concerthub.errors.NotFoundResponseBody.new(
                detail="Ticket not found for refund"
            ).model_dump(),
        )
    return schema.responses.concerthub.ActionMessageResponseBody.create(
        message="Ticket refunded"
    )


@concerthub_router.get(
    "/staff/sales-monitoring",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.GetSalesMonitoringResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
    },
)
async def get_sales_monitoring(
    token: Annotated[str, Header()],
    promoter_name: str | None = None,
    venue_name: str | None = None,
) -> schema.responses.concerthub.GetSalesMonitoringResponseBody | JSONResponse:
    try:
        items = await dependency.manage_concerthub.get_sales_monitoring(
            token=token,
            promoter_name=promoter_name,
            venue_name=venue_name,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    return schema.responses.concerthub.GetSalesMonitoringResponseBody.create(
        items=items
    )


@concerthub_router.get(
    "/staff/venues-config",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.GetVenuesConfigResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
    },
)
async def get_venues_config(
    token: Annotated[str, Header()],
) -> schema.responses.concerthub.GetVenuesConfigResponseBody | JSONResponse:
    try:
        items = await dependency.manage_concerthub.get_venues_configuration(token=token)
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    return schema.responses.concerthub.GetVenuesConfigResponseBody.create(items=items)


@concerthub_router.post(
    "/staff/concerts",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.responses.concerthub.CreateConcertResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": schema.responses.concerthub.errors.ValidationErrorResponseBody
        },
    },
)
async def create_concert(
    token: Annotated[str, Header()],
    body: schema.requests.concerthub.CreateConcertRequestBody,
) -> schema.responses.concerthub.CreateConcertResponseBody | JSONResponse:
    try:
        concert_id = await dependency.manage_concerthub.create_concert(
            token=token,
            program_name=body.program_name,
            start_datetime=body.start_datetime,
            age_restriction=body.age_restriction,
            artist_id=body.artist_id,
            venue_id=body.venue_id,
            promoter_id=body.promoter_id,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    except concerthub_errors.ValidationError:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=schema.responses.concerthub.errors.ValidationErrorResponseBody.new(
                detail="Invalid concert data"
            ).model_dump(),
        )
    return schema.responses.concerthub.CreateConcertResponseBody.create(
        concert_id=concert_id
    )


@concerthub_router.post(
    "/staff/tickets/release",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.responses.concerthub.ReleaseTicketsResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "model": schema.responses.concerthub.errors.ValidationErrorResponseBody
        },
    },
)
async def release_tickets(
    token: Annotated[str, Header()],
    body: schema.requests.concerthub.ReleaseTicketsRequestBody,
) -> schema.responses.concerthub.ReleaseTicketsResponseBody | JSONResponse:
    try:
        barcodes = await dependency.manage_concerthub.release_tickets(
            token=token,
            concert_id=body.concert_id,
            sector_id=body.sector_id,
            price=body.price,
            count=body.count,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    except concerthub_errors.ValidationError:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=schema.responses.concerthub.errors.ValidationErrorResponseBody.new(
                detail="Sector capacity exceeded or invalid parameters"
            ).model_dump(),
        )
    return schema.responses.concerthub.ReleaseTicketsResponseBody.create(
        barcodes=barcodes
    )


@concerthub_router.post(
    "/staff/gate-control",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.ScanGateTicketResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schema.responses.concerthub.errors.NotFoundResponseBody
        },
    },
)
async def scan_gate_ticket(
    token: Annotated[str, Header()],
    body: schema.requests.concerthub.ScanTicketRequestBody,
) -> schema.responses.concerthub.ScanGateTicketResponseBody | JSONResponse:
    try:
        item = await dependency.manage_concerthub.scan_gate_ticket(
            token=token,
            barcode=body.barcode,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    except concerthub_errors.NotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=schema.responses.concerthub.errors.NotFoundResponseBody.new(
                detail="Ticket barcode not found"
            ).model_dump(),
        )
    return schema.responses.concerthub.ScanGateTicketResponseBody.create(item=item)


@concerthub_router.get(
    "/admin/artist-popularity",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.GetArtistPopularityResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
    },
)
async def get_artist_popularity(
    token: Annotated[str, Header()],
    genre: str | None = None,
) -> schema.responses.concerthub.GetArtistPopularityResponseBody | JSONResponse:
    try:
        items = await dependency.manage_concerthub.get_artist_popularity(
            token=token,
            genre=genre,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    return schema.responses.concerthub.GetArtistPopularityResponseBody.create(
        items=items
    )


@concerthub_router.get(
    "/admin/tables",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.GetAllTablesResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
    },
)
async def get_all_tables(
    token: Annotated[str, Header()],
) -> schema.responses.concerthub.GetAllTablesResponseBody | JSONResponse:
    try:
        tables = await dependency.manage_concerthub.get_all_tables_list(token=token)
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    return schema.responses.concerthub.GetAllTablesResponseBody.create(tables=tables)


@concerthub_router.get(
    "/admin/tables/{table_name}",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.GetTableDataResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
    },
)
async def get_table_data(
    token: Annotated[str, Header()],
    table_name: str,
) -> schema.responses.concerthub.GetTableDataResponseBody | JSONResponse:
    try:
        rows = await dependency.manage_concerthub.get_table_data(
            token=token,
            table_name=table_name,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    return schema.responses.concerthub.GetTableDataResponseBody.create(rows=rows)


@concerthub_router.delete(
    "/admin/tables/{table_name}/{record_id}",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.ActionMessageResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schema.responses.concerthub.errors.NotFoundResponseBody
        },
    },
)
async def delete_table_record(
    token: Annotated[str, Header()],
    table_name: str,
    record_id: int,
) -> schema.responses.concerthub.ActionMessageResponseBody | JSONResponse:
    try:
        await dependency.manage_concerthub.delete_table_record(
            token=token,
            table_name=table_name,
            record_id=record_id,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    except concerthub_errors.NotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=schema.responses.concerthub.errors.NotFoundResponseBody.new(
                detail="Record not found"
            ).model_dump(),
        )
    return schema.responses.concerthub.ActionMessageResponseBody.create(
        message="Record deleted"
    )


@concerthub_router.get(
    "/admin/audit-logs",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.GetAuditLogsResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
    },
)
async def get_audit_logs(
    token: Annotated[str, Header()],
    operation_type: str | None = None,
) -> schema.responses.concerthub.GetAuditLogsResponseBody | JSONResponse:
    try:
        logs = await dependency.manage_concerthub.get_audit_logs(
            token=token,
            operation_type=operation_type,
        )
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    return schema.responses.concerthub.GetAuditLogsResponseBody.create(logs=logs)


@concerthub_router.get(
    "/admin/secret-data",
    status_code=status.HTTP_200_OK,
    response_model=schema.responses.concerthub.GetSecretDataResponseBody,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "model": schema.responses.concerthub.errors.UnauthorizedResponseBody
        },
        status.HTTP_403_FORBIDDEN: {
            "model": schema.responses.concerthub.errors.PermissionDeniedResponseBody
        },
    },
)
async def get_secret_data(
    token: Annotated[str, Header()],
) -> schema.responses.concerthub.GetSecretDataResponseBody | JSONResponse:
    try:
        items = await dependency.manage_concerthub.get_secret_data(token=token)
    except concerthub_errors.UnauthorizedError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=schema.responses.concerthub.errors.UnauthorizedResponseBody.new(
                detail="Unauthorized"
            ).model_dump(),
        )
    except concerthub_errors.PermissionDeniedError:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=schema.responses.concerthub.errors.PermissionDeniedResponseBody.new(
                detail="Access denied for caller"
            ).model_dump(),
        )
    return schema.responses.concerthub.GetSecretDataResponseBody.create(items=items)
