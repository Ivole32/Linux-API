from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from core_functions.limiter import limiter

router = APIRouter()

@router.get(
    "/",
    tags=["General"],
    description="The landing endpoint of the API. It returns a message with the documentation link.",
    responses={
        200: {"description": "The server works"}
    }
)
@limiter.limit("10/minute")
def landing_page(request: Request):
    return JSONResponse(content={
            "message": "Docs at /docs",
            "doc-link": "/docs"
        })