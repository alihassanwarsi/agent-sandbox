from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from app.observability.tracing import build_tracer_provider
from app.observability.trace_node import traced_node


def test_traced_node_records_a_span_with_the_correct_name():
    exporter = InMemorySpanExporter()
    provider = build_tracer_provider(exporters=[exporter])
    tracer = provider.get_tracer("test")

    def dummy_node(state):
        return {"selected_tool": "calculator"}

    wrapped = traced_node(tracer, "plan", dummy_node)
    wrapped({"user_message": "hi"})

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "plan"


def test_traced_node_records_selected_tool_attribute():
    exporter = InMemorySpanExporter()
    provider = build_tracer_provider(exporters=[exporter])
    tracer = provider.get_tracer("test")

    def dummy_node(state):
        return {"selected_tool": "create_ticket"}

    wrapped = traced_node(tracer, "plan", dummy_node)
    wrapped({})

    spans = exporter.get_finished_spans()
    assert spans[0].attributes["tool.selected"] == "create_ticket"


def test_traced_node_records_blocked_attribute_when_permission_denied():
    exporter = InMemorySpanExporter()
    provider = build_tracer_provider(exporters=[exporter])
    tracer = provider.get_tracer("test")

    def dummy_node(state):
        return {"permission_error": "not allowed"}

    wrapped = traced_node(tracer, "permission_check", dummy_node)
    wrapped({})

    spans = exporter.get_finished_spans()
    assert spans[0].attributes["blocked"] is True


def test_traced_node_records_exception_and_reraises():
    import pytest

    exporter = InMemorySpanExporter()
    provider = build_tracer_provider(exporters=[exporter])
    tracer = provider.get_tracer("test")

    def failing_node(state):
        raise ValueError("something broke")

    wrapped = traced_node(tracer, "execution", failing_node)

    with pytest.raises(ValueError):
        wrapped({})

    spans = exporter.get_finished_spans()
    assert spans[0].status.status_code.name == "ERROR"
    assert any(event.name == "exception" for event in spans[0].events)