from opentelemetry.trace import Status, StatusCode

def traced_node(tracer, node_name: str, node_fn):
    """Return a version of node_fn that runs inside a traced span."""

    def wrapped(state):
        with tracer.start_as_current_span(node_name) as span:
            span.set_attribute("node.name", node_name)

            try:
                result = node_fn(state)
            except Exception as exc:
                span.record_exception(exc)
                span.set_status(Status(StatusCode.ERROR, str(exc)))
                raise

            if isinstance(result, dict):
                if result.get("selected_tool"):
                    span.set_attribute("tool.selected", result["selected_tool"])
                if result.get("permission_error"):
                    span.set_attribute("blocked", True)
                if result.get("confirmation_error"):
                    span.set_attribute("confirmation_required", True)
                if result.get("awaiting_approval"):
                    span.set_attribute("awaiting_approval", True)

            return result

    return wrapped