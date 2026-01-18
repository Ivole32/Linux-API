"""
Main configuration file for the API.
"""

# OS and path utilities
import os
from pathlib import Path

# Environment variable loader
from dotenv import load_dotenv

# Load environment variables from .env file
ROOT_DIR = Path(__file__).resolve().parent.parent  # Go up to root directory
load_dotenv(ROOT_DIR / ".env") # Load .env file

# Secrets
API_KEY_SECRET = os.getenv("API_KEY_SECRET", None) # Use None if not set in .env to raise error later


# API configuration
API_TITLE = "Linux API" # Short title for the API
API_DESCRIPTION = "A linux API server to get system informations and other live informations about your linux machine.." # Description of the API
API_VERSION = "dev" # Version of the API
API_PREFIX = f"/api/{API_VERSION}" # Prefix for all API endpoints
API_DOCS_ENABLED = True # Enable or disable API documentation

# PostgreSQL configuration
# (Floats must stay as floats)
POSTGRES_HOST = "127.0.0.1" # Hostname of the PostgreSQL server (Docker Compose service name)
POSTGRES_PORT = 5432 # Port number of the PostgreSQL server
POSGRES_USER = os.getenv("POSTGRES_USER", None)  # Use None if not set in .env to raise error later
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", None)  # Use None if not set in .env to raise error later
POSTGRES_DATABSE = os.getenv("POSTGRES_DATABASE", None)  # Use None if not set in .env to raise error later
POSGRES_MIN_CONNECTIONS = 1 # Minimum number of connections in the pool
POSTGRES_MAX_CONNECTIONS = 5 # Maximum number of connections in the pool
POSTGRES_CONNECT_TIMEOUT = 5.0 # Connection timeout for PostgreSQL (in seconds)
POSTGRES_RETRIES = 3 # Number of retries for PostgreSQL connection
POSTGRES_RETRY_DELAY = 2.0 # Delay between PostgreSQL connection retries (in seconds)
POSTGRES_HEALTHCHECK_TIMEOUT = 15.0 # Timeout for PostgreSQL health checks (in seconds)

# CORS configuration
CORS_ALLOWED_ORIGINS = ["*"] # Allow all origins for now, can be adjusted later
CORS_ALLOWED_METHODS = ["GET", "POST", "PUT","PATCH", "DELETE", "OPTIONS"] # Only allow specific methods, can be adjusted later
CORS_ALLOWED_HEADERS = ["*"] # Allow all headers
CORS_MAX_AGE = 600 # Cache preflight (OPTIONS) requests for 10 minutes