from functools import wraps

from .._exceptions import UnauthorizedError


def handle_refresh_token(method):
    """
    Decorator to handle automatic token refresh on 401 Unauthorized errors.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            # First attempt to call the original method
            return method(self, *args, **kwargs)
        except UnauthorizedError:  # Assume ArtifactClient raises this for 401 errors
            # Refresh the token using the IAMClient
            self.iam_client.refresh_token()
            # Retry the original method
            return method(self, *args, **kwargs)

    return wrapper
