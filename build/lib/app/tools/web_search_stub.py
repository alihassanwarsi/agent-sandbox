from pydantic import BaseModel, Field
from app.tools.registry import Tool

class WebSearchInput(BaseModel):
    """Input for the web search tool."""
    query: str = Field(..., min_length=1, description="The search query text.")

class WebSearchResult(BaseModel):
    """One fake search result."""
    title: str
    snippet: str
    url: str

def search_web(data: WebSearchInput) -> list[WebSearchResult]:
    """Return fake search results for the given query. Always labeled
    clearly as placeholder data."""

    return [
        WebSearchResult(
            title=f"[STUB RESULT 1] Information about '{data.query}'",
            snippet=(
                f"This is placeholder text standing in for a real search "
                f"result about '{data.query}'. No real web search happened."
            ),
            url="https://example.com/stub-result-1",
        ),
        WebSearchResult(
            title=f"[STUB RESULT 2] More on '{data.query}'",
            snippet=(
                f"Another placeholder result for '{data.query}'. Replace "
                f"this tool with a real search API when needed."
            ),
            url="https://example.com/stub-result-2",
        ),
    ]

WEB_SEARCH_STUB_TOOL = Tool(
    name="web_search",
    description="Returns placeholder search results (stub, no real internet access).",
    input_schema=WebSearchInput,
    handler=search_web,
)