"""
Middleware to handle CORS (Cross-Origin Resource Sharing).
"""

# FastAPI CORS middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

# CORS settings from config
from api.config.config import CORS_ALLOWED_ORIGINS, CORS_ALLOWED_METHODS, CORS_ALLOWED_HEADERS, CORS_MAX_AGE


def setup_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware.
    """

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=CORS_ALLOWED_METHODS, # Only allow specific methods, can be adjusted later
        allow_headers=CORS_ALLOWED_HEADERS,
        max_age=CORS_MAX_AGE
    )

    return app