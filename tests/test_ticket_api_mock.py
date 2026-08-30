from app.tools.mock_ticket_api import CreateTicketInput, create_ticket, TICKET_API_MOCK_TOOL

def test_creates_a_ticket_with_correct_details():
    result = create_ticket(
        CreateTicketInput(title="Login broken", description="Cannot log in with correct password.")
    )
    assert result.title == "Login broken"
    assert result.description == "Cannot log in with correct password."
    assert result.status == "open"

def test_ticket_id_has_expected_format():
    result = create_ticket(CreateTicketInput(title="Test", description="Test issue."))
    assert result.ticket_id.startswith("TICKET-")

def test_each_ticket_gets_a_unique_id():
    result_one = create_ticket(CreateTicketInput(title="Issue 1", description="First issue."))
    result_two = create_ticket(CreateTicketInput(title="Issue 2", description="Second issue."))
    assert result_one.ticket_id != result_two.ticket_id

def test_tool_metadata_is_correct():
    assert TICKET_API_MOCK_TOOL.name == "create_ticket"
    assert TICKET_API_MOCK_TOOL.input_schema is CreateTicketInput