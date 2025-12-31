"""Exceptions related to authentication/session state."""


class SessionExpired(Exception):
    """Raised when the current Themis session is no longer authenticated.

    This typically happens when cookies expire or the server redirects to the
    login flow.
    """

class SessionRefreshed(Exception):
    """Raised when the session cookies have been refreshed.

    This is mainly used internally to signal that the session should be retried.
    """