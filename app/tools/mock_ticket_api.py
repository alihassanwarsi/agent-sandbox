import uuid
from pydantic import BaseModel, Field
from app.tools.registry import Tool

class CreateTicketInput(BaseModel):
    """Input for the ticket creation tool."""
    title: str = Field(..., min_length=1, description="Short title for the ticket.")
    description: str = Field(..., min_length=1, description="Details about the issue.")

class TicketResult(BaseModel):
    """The result of creating a ticket."""
    ticket_id: str
    title: str
    description: str
    status: str

def create_ticket(data: CreateTicketInput) -> TicketResult:
    """Simulate creating a ticket and return a fake confirmation."""

    fake_ticket_id = f"TICKET-{uuid.uuid4().hex[:8].upper()}"

    return TicketResult(
        ticket_id=fake_ticket_id,
        title=data.title,
        description=data.description,
        status="open",
    )

TICKET_API_MOCK_TOOL = Tool(
    name="create_ticket",
    description="Simulates creating a support ticket (mock, no real service is called).",
    input_schema=CreateTicketInput,
    handler=create_ticket,
)