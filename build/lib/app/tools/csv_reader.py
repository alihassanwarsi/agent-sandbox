import csv
from pathlib import Path
from pydantic import BaseModel, Field
from app.tools.file_reader import SANDBOX_DIR
from app.tools.registry import Tool

class CSVReaderInput(BaseModel):
    """Input for the CSV reader tool."""
    filename: str = Field(..., min_length=1, description="CSV file to read, e.g. 'people.csv'.")
    filter_column: str | None = Field(default=None, description="Optional column name to filter by.")
    filter_value: str | None = Field(default=None, description="Optional value that filter_column must equal.")

def _resolve_safe_path(filename: str) -> Path:
    """Make sure the requested file is really inside SANDBOX_DIR."""

    requested_path = (SANDBOX_DIR / filename).resolve()

    if not requested_path.is_relative_to(SANDBOX_DIR):
        raise PermissionError(f"Access denied: '{filename}' is outside the allowed folder.")
    
    if not requested_path.exists():
        raise FileNotFoundError(f"File '{filename}' does not exist.")
    
    return requested_path

def read_csv(data: CSVReaderInput) -> list[dict[str, str]]:
    """Read a CSV file and optionally filter rows by column value."""

    path = _resolve_safe_path(data.filename)

    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    if data.filter_column is None:
        return rows

    if rows and data.filter_column not in rows[0]:
        raise ValueError(f"Column '{data.filter_column}' does not exist in '{data.filename}'.")

    filtered_rows = []

    for row in rows:
        if row.get(data.filter_column) == data.filter_value:
            filtered_rows.append(row)

    return filtered_rows

CSV_READER_TOOL = Tool(
    name="csv_reader",
    description="Reads a CSV file from the sandbox folder, with optional column filtering.",
    input_schema=CSVReaderInput,
    handler=read_csv,
)