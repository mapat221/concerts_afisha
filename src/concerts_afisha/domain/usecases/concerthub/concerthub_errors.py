class ConcertHubError(Exception):
    pass


class UnauthorizedError(ConcertHubError):
    pass


class PermissionDeniedError(ConcertHubError):
    pass


class NotFoundError(ConcertHubError):
    pass


class ValidationError(ConcertHubError):
    pass
