"""Custom exceptions for Rika Firenet integration."""


class RikaFirenetError(Exception):
    """Base exception for Rika Firenet integration."""


class RikaAuthenticationError(RikaFirenetError):
    """Exception raised when authentication fails."""


class RikaApiError(RikaFirenetError):
    """Exception raised when API communication fails."""


class RikaConnectionError(RikaFirenetError):
    """Exception raised when connection to Rika servers fails."""


class RikaTimeoutError(RikaFirenetError):
    """Exception raised when request times out."""


class RikaValidationError(RikaFirenetError):
    """Exception raised when data validation fails."""
