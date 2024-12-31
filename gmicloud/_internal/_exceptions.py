class APIError(Exception):
    """
    Generic exception for API-related errors.
    """
    pass


class UploadFileError(Exception):
    """
    Exception for file upload errors.
    """
    pass


class UnauthorizedError(Exception):
    """
    Exception for unauthorized access errors.
    """
    pass
