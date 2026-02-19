"""
Utitities to check class readiness
"""

from fastapi import HTTPException, status
from typing import Any

def ensure_class_ready(
        obj: Any,
        *,
        check: str = "is_ready",
        name: str | None = None
) -> bool:
    """
    Ensure that an object reports itself as ready.

    The function calls a readiness method (by default ``is_ready()``) on the
    given object. The method must return either:

    - ``bool``  
      Indicates whether the object is ready.
    - ``(bool, str)``  
      A tuple where the first element indicates readiness and the second
      element provides an optional status or reason message.

    If the object is not ready, an HTTP 503 error is raised. If the readiness
    method does not exist or is not callable, an HTTP 501 error is raised.

    Args:
        obj: The object to check for readiness.
        check: Name of the readiness method to call (default: ``"is_ready"``).
        name: Optional human-readable name used in error messages.
              Defaults to the object's class name.

    Returns:
        True if the object is ready.

    Raises:
        HTTPException:
            - 501 Not Implemented Error if the readiness method is missing
              or not callable.
            - 503 Service Unavailable if the object reports it is not ready.
              The optional status message is included in the response.
    """

    checker = getattr(obj, check, None)

    # Get the readiness checker method and raise 501 if missing
    if not callable(checker):
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{name or obj.__class__.__name__} has no '{check}()' method"
        )
    
    # Call the checker method
    result = checker()

    # Parse the result
    if isinstance(result, tuple): # If boolean with message
        ready, message = result[0], result[1] if len(result) > 1 else None
    else: # Just boolean
        ready, message = bool(result), None

    # If not ready, raise 503 with optional message
    if not ready:
        detail = (
            f"{name or obj.__class__.__name__} not ready"
            + (f": {message}" if message else "")
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )
    
    return True