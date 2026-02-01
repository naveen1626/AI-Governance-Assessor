import httpx
from bs4 import BeautifulSoup
from pypdf import PdfReader
import tempfile
import re
import io
from app.models import URLFetchResponse


async def fetch_and_parse(url: str) -> URLFetchResponse:
    """Fetch URL and extract title + abstract"""
    try:
        # Determine URL type and handle accordingly
        if "arxiv.org" in url:
            return await parse_arxiv(url)
        elif url.endswith(".pdf"):
            return await parse_pdf_url(url)
        else:
            return await parse_html_page(url)
    except Exception as e:
        return URLFetchResponse(
            title="",
            abstract="",
            success=False,
            error=f"Failed to fetch/parse: {str(e)}"
        )


async def parse_arxiv(url: str) -> URLFetchResponse:
    """Parse arXiv page for title and abstract"""
    # Convert PDF URL to abstract page if needed
    if "/pdf/" in url:
        url = url.replace("/pdf/", "/abs/").replace(".pdf", "")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title
    title_elem = soup.find("h1", class_="title")
    title = ""
    if title_elem:
        title = title_elem.get_text().replace("Title:", "").strip()

    # Extract abstract
    abstract_elem = soup.find("blockquote", class_="abstract")
    abstract = ""
    if abstract_elem:
        abstract = abstract_elem.get_text().replace("Abstract:", "").strip()

    if not title and not abstract:
        return URLFetchResponse(
            title="",
            abstract="",
            success=False,
            error="Could not extract title/abstract from arXiv page"
        )

    return URLFetchResponse(
        title=title,
        abstract=abstract,
        success=True
    )


async def parse_pdf_url(url: str) -> URLFetchResponse:
    """Download PDF and extract title + abstract"""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, timeout=60.0)
        response.raise_for_status()

    # Parse PDF from bytes
    return parse_pdf_bytes(response.content)


def parse_pdf_bytes(pdf_bytes: bytes) -> URLFetchResponse:
    """Extract title and abstract from PDF bytes"""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))

        # Get text from first two pages
        text = ""
        for i, page in enumerate(reader.pages[:2]):
            text += page.extract_text() or ""

        # Try to extract title (usually first non-empty line)
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        title = lines[0] if lines else ""

        # Try to find abstract section
        abstract = ""
        abstract_match = re.search(
            r"abstract[:\s]*(.+?)(?:introduction|keywords|1\.|1\s+introduction|index terms)",
            text,
            re.IGNORECASE | re.DOTALL
        )
        if abstract_match:
            abstract = abstract_match.group(1).strip()
            # Clean up whitespace
            abstract = re.sub(r"\s+", " ", abstract)

        if not title and not abstract:
            return URLFetchResponse(
                title="",
                abstract="",
                success=False,
                error="Could not extract title/abstract from PDF"
            )

        return URLFetchResponse(
            title=title,
            abstract=abstract,
            success=True
        )
    except Exception as e:
        return URLFetchResponse(
            title="",
            abstract="",
            success=False,
            error=f"PDF parsing error: {str(e)}"
        )


async def parse_html_page(url: str) -> URLFetchResponse:
    """Parse generic HTML page for title and abstract"""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, timeout=30.0)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Try common title patterns
    title = ""
    for selector in ["h1", "title", ".paper-title", ".article-title"]:
        elem = soup.select_one(selector)
        if elem:
            title = elem.get_text().strip()
            break

    # Try common abstract patterns
    abstract = ""
    for selector in [".abstract", "#abstract", "[class*='abstract']", "p.abstract"]:
        elem = soup.select_one(selector)
        if elem:
            abstract = elem.get_text().strip()
            break

    # Fallback: look for text containing "abstract"
    if not abstract:
        for p in soup.find_all("p"):
            text = p.get_text()
            if text.lower().startswith("abstract"):
                abstract = text
                break

    return URLFetchResponse(
        title=title,
        abstract=abstract,
        success=bool(title or abstract),
        error=None if (title or abstract) else "Could not extract content from page"
    )
