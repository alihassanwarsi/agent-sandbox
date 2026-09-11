from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

def build_tracer_provider(exporter=None) -> TracerProvider:
    """Build a TracerProvider using the given exporter (defaults to printing to the console)."""

    if exporter is None:
        exporter = ConsoleSpanExporter()

    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider