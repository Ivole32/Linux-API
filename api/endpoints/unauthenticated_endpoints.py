from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from core_functions.limiter import limiter

router = APIRouter()

@router.get(
    "/",
    tags=["Public"],
    description="Welcome to Linux-API. Use `/docs` for interactive API documentation.",
    responses={
        200: {
            "description": "Landing page",
            "content": {
                "application/json": {
                    "examples": {
                        "Success": {
                            "summary": "Landing page",
                            "value": {
                                "detail": "Welcome to Linux-API"
                            }
                        }
                    }
                }
            }
        }
    }
)
@limiter.limit("10/minute")
def landing_page(request: Request):
    return JSONResponse(content={
            "message": "Docs at /docs",
            "doc-link": "/docs"
        })