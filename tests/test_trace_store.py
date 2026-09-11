from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from app.observability.tracing import build_tracer_provider
from app.observability.trace_store import InMemoryTraceStore
from app.observability.trace_viewer import format_trace

def test_trace_store_groups_spans_by_trace_id():
    store = InMemoryTraceStore()
    provider = build_tracer_provider(exporters=[store])
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("parent") as parent:
        with tracer.start_as_current_span("child"):
            pass

    trace_id = format(parent.get_span_context().trace_id, "032x")
    spans = store.get_trace(trace_id)

    assert len(spans) == 2
    names = {span.name for span in spans}
    assert names == {"parent", "child"}

def test_trace_store_returns_empty_list_for_unknown_trace():
    store = InMemoryTraceStore()
    assert store.get_trace("does-not-exist") == []

def test_format_trace_produces_readable_summary():
    store = InMemoryTraceStore()
    provider = build_tracer_provider(exporters=[store])
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("plan") as span:
        span.set_attribute("tool.selected", "calculator")

    trace_id = format(span.get_span_context().trace_id, "032x")
    summary = format_trace(store, trace_id)

    assert "plan" in summary
    assert "calculator" in summary

def test_format_trace_handles_unknown_trace_id():
    store = InMemoryTraceStore()
    summary = format_trace(store, "does-not-exist")
    assert "No trace found" in summary