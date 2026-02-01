class UserDeletionError(Exception):
    """Raised when an error occured while deletion user."""
    pass

class UserCreationError(Exception):
    """Parent class for all user creation errors."""
    pass

class UserRecordCreationError(UserCreationError):
    """Raised when user record could not be created."""
    pass

class UserAuthCreationError(UserCreationError):
    """Raised when user auth record could not be created."""

class UserPermEditError(Exception):
    """Raised when user perm record could not be set."""
    pass

class UserRecordReadError(Exception):
    """Raised when user record could not be read."""

class UserPermReadError(Exception):
    """Raised when user perm could not be read."""

class UserNotFoundError(Exception):
    """Raised when an user is not found in the database."""
    pass

class NoRowsAffected(Exception):
    """Raised when no rows are affected in postsql query."""
    pass

class NoUserDeleted(NoRowsAffected):
    """Raised when no user is deleted"""
    pass

class LastAdminError(Exception):
    """Raised when attemping to remove the final active admin."""
    pass