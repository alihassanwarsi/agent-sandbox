from app.tools.web_search_stub import WebSearchInput, search_web, WEB_SEARCH_STUB_TOOL

def test_search_returns_two_results():
    results = search_web(WebSearchInput(query="python testing"))
    assert len(results) == 2

def test_results_mention_the_query():
    results = search_web(WebSearchInput(query="agent sandbox"))
    for result in results:
        assert "agent sandbox" in result.title or "agent sandbox" in result.snippet

def test_results_are_clearly_labeled_as_stub():
    results = search_web(WebSearchInput(query="anything"))
    for result in results:
        assert "STUB" in result.title

def test_results_have_valid_looking_urls():
    results = search_web(WebSearchInput(query="anything"))
    for result in results:
        assert result.url.startswith("https://")

def test_tool_metadata_is_correct():
    assert WEB_SEARCH_STUB_TOOL.name == "web_search"
    assert WEB_SEARCH_STUB_TOOL.input_schema is WebSearchInput