from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

def build_tracer_provider(exporters=None) -> TracerProvider:
    """Build a TracerProvider using the given exporters (defaults to printing to the console)."""

    if exporters is None:
        exporters = [ConsoleSpanExporter()]

    provider = TracerProvider()
    for exporter in exporters:
        provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider