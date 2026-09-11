from app.observability.trace_store import InMemoryTraceStore

def format_trace(store: InMemoryTraceStore, trace_id: str) -> str:
    """Return a readable, step-by-step summary of one trace."""

    spans = store.get_trace(trace_id)
    if not spans:
        return f"No trace found for id '{trace_id}'."

    spans = sorted(spans, key=lambda s: s.start_time)

    lines = [f"Trace {trace_id}:"]
    for span in spans:
        duration_ms = (span.end_time - span.start_time) / 1_000_000
        attributes = dict(span.attributes or {})
        status = "ERROR" if span.status.status_code.name == "ERROR" else "ok"

        lines.append(f"  - {span.name} ({duration_ms:.1f}ms, {status}) {attributes}")

    return "\n".join(lines)