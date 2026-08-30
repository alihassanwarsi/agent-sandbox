from app.tools.registry import ToolRegistry
from app.tools.calculator import CALCULATOR_TOOL
from app.tools.csv_reader import CSV_READER_TOOL
from app.tools.file_reader import FILE_READER_TOOL
from app.tools.mock_ticket_api import TICKET_API_MOCK_TOOL
from app.tools.web_search_stub import WEB_SEARCH_STUB_TOOL

def build_default_registry() -> ToolRegistry:
    """Create a ToolRegistry containing all 5 starter tools."""

    registry = ToolRegistry()
    registry.register(CALCULATOR_TOOL)
    registry.register(FILE_READER_TOOL)
    registry.register(WEB_SEARCH_STUB_TOOL)
    registry.register(CSV_READER_TOOL)
    registry.register(TICKET_API_MOCK_TOOL)
    return registry