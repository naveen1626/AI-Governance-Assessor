from fastapi import APIRouter, HTTPException
from app.models import URLFetchRequest, URLFetchResponse
from app.services.url_parser import fetch_and_parse

router = APIRouter()


@router.post("/fetch-url", response_model=URLFetchResponse)
async def fetch_url(request: URLFetchRequest):
    """Fetch and parse a URL to extract title and abstract"""
    result = await fetch_and_parse(request.url)

    if not result.success:
        # Still return the response (with error) rather than raising
        # This allows frontend to show the error and suggest manual entry
        pass

    return result
