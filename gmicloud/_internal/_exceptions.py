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



def formated_exception(error: Exception) -> dict:
    """
    Formats the exception message for logging.

    :param error: The exception to format.
    :return: A dictionary containing the error code and message.
    """
    message = str(error).split(":")[1]
    status = str(message).split(" - ")[0] if " - " in str(message) else "0"
    error_message = str(message).split(" - ")[1] if " - " in str(message) else str(message)
    return {
        "code": status,
        "error": error_message
    }