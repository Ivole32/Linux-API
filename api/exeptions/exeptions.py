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
    pass

class UserPermEditError(Exception):
    """Raised when user perm record could not be set."""
    pass

class UserRecordReadError(Exception):
    """Raised when user record could not be read."""
    pass

class UserPermReadError(Exception):
    """Raised when user perm could not be read."""
    pass

class DatabaseFlushError(Exception):
    """Raised when database could not be flushed"""
    pass

class UserNotFoundError(Exception):
    """Raised when an user is not found in the database."""
    pass

class NoRowsAffected(Exception):
    """Raised when no rows are affected in postsql query."""
    pass

class NoUserDeleted(NoRowsAffected):
    """Raised when no user is deleted"""
    pass

class NoUserAuthCreatedError(NoRowsAffected):
    """Raised when no user auth record is created"""
    pass

class NoUserPermEditedError(NoRowsAffected):
    """Raised when no user perm record is edited"""
    pass

class LastAdminError(Exception):
    """Raised when attemping to remove the final active admin."""
    pass

class KeyHashError(Exception):
    """Raised when an API key could not be hashed"""
    pass

class APIKeyLookupError(Exception):
    """Raised when an unexpected error happens while checking for api key existence"""
    pass

class APIKeyEmptyError(Exception):
    """Raised when an empty API key is sen dto the server via a header value"""
    pass

class NoChangesNeeded(Exception):
    """Raised when a database operation would not change any data"""
    pass

class ImmutableException(Exception):
    """Raised when database column is immutable"""
    pass

class UserImmutableChangeError(Exception):
    """Raised when user could not be made immutable"""
    pass