"""
Main configuration file for the API.
"""

# OS and path utilities
import os
from pathlib import Path

# Environment variable loader
from dotenv import load_dotenv

# Load environment variables from .env file
# This approach is not working anymore (idk why)
#ROOT_DIR = Path(__file__).resolve().parent.parent  # Go up to root directory
#load_dotenv(ROOT_DIR / ".env") # Load .env file
load_dotenv()

# Secrets
API_KEY_SECRET = os.getenv("API_KEY_SECRET", None) # Use None if not set in .env to raise error later

ENABLE_LEGACY_ROUTES = True

# Demo Mode
DEMO_MODE = False
RESET_DATABASE_WHEN_DEMO = True

# API configuration
API_TITLE = "Linux API" # Short title for the API
API_DESCRIPTION = "A Linux API server to get system information and other live information about your Linux machine." # Description of the API
API_VERSION = "v1" # Version of the API
API_PREFIX = f"/api/{API_VERSION}" # Prefix for all API endpoints
LEGACY_API_PREFIX = f"/api/legacy" # Prefix for old legacy routes
API_DOCS_ENABLED = True # Enable or disable API documentation

ALLOWED_HOSTS = ["*"]

ROUTE_DISABLE_CONFIG = [] # Specific routes that ar disabled for example f"/api/{API_VERSION}/system/info/processes"
ROUTE_DISABLED_REASON = "The route is currenty disabled." # The reason why the route is disabled
ROUTE_DISABLED_RETRY_AFTER = 600 # A value in seconds after what time the client can retry to use the route

# Rate limiting configuration
API_RATE_LIMIT_ENABLED = True # Enable or disable rate limiting
API_DEFAULT_RATE_LIMITS = ["100/minute"] # Default rate limits

# User configuration
USERNAME_MIN_LENGTH = 4
USERNAME_MAX_LENGTH = 12

# PostgreSQL configuration
# (Floats must stay as floats)
POSTGRES_HOST = "127.0.0.1" # Hostname of the PostgreSQL server (Docker Compose service name)
POSTGRES_PORT = 5432 # Port number of the PostgreSQL server
POSTGRES_USER = os.getenv("POSTGRES_USER", None)  # Use None if not set in .env to raise error later
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", None)  # Use None if not set in .env to raise error later
POSTGRES_DATABASE = os.getenv("POSTGRES_DB", None)  # Use None if not set in .env to raise error later
POSTGRES_MIN_CONNECTIONS = 1 # Minimum number of connections in the pool
POSTGRES_MAX_CONNECTIONS = 5 # Maximum number of connections in the pool
POSTGRES_CONNECT_TIMEOUT = 5.0 # Connection timeout for PostgreSQL (in seconds)
POSTGRES_RETRIES = 2 # Number of retries for PostgreSQL connection
POSTGRES_RETRY_DELAY = 2.0 # Delay between PostgreSQL connection retries (in seconds)
POSTGRES_HEALTHCHECK_TIMEOUT = 15.0 # Timeout for PostgreSQL health checks (in seconds)
POSTGRES_HEALTHCHECK_INTERVALL = 5.0 # Intervall time for PostgreSQL healthcheck (in seconds)

# CORS configuration
CORS_ALLOWED_ORIGINS = ["*"] # Allow all origins for now, can be adjusted later
CORS_ALLOWED_METHODS = ["GET", "POST", "DELETE", "OPTIONS"] # Only allow specific methods, can be adjusted later
CORS_ALLOWED_HEADERS = ["*"] # Allow all headers
CORS_MAX_AGE = 600 # Cache preflight (OPTIONS) requests for 10 minutes

# Database migration
BACKUP_DATABASE_BEFORE_MIGRATION = True # Recommended because migrations can break much stuff
BACKUP_DATABASE_AT_STARTUP = False # True if a backup is needed after every server start
DATABASE_BACKUP_DIR = r"C:\Users\<not_for_you>\Documents\GitHub\Linux-API\backup"
AUTO_MIGRATE_DATABASE_ON_STARTUP = True
ALEMBIC_INI_FILE = r"C:\Users\<not_for_you>\Documents\GitHub\Linux-API\alembic.ini"