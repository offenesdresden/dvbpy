class DVBError(Exception):
    """Base exception for all dvb errors."""


class APIError(DVBError):
    """API returned an error, non-200 status, or Status.Code != 'Ok'."""


class ConnectionError(DVBError):  # noqa: A001
    """Network failure or timeout."""
