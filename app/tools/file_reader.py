from pathlib import Path
from pydantic import BaseModel, Field
from app.tools.registry import Tool

SANDBOX_DIR = Path("sandbox_files").resolve()

class FileReaderInput(BaseModel):
    """Input for the file reader tool."""
    filename: str = Field(..., min_length=1, description="Name of the file to read, e.g. 'hello.txt'.")

def read_file(data: FileReaderInput) -> str:
    """Read a file's contents, but only if it's inside SANDBOX_DIR."""

    requested_path = (SANDBOX_DIR / data.filename).resolve()

    if not requested_path.is_relative_to(SANDBOX_DIR):
        raise PermissionError(f"Access denied: '{data.filename}' is outside the allowed folder.")

    if not requested_path.exists():
        raise FileNotFoundError(f"File '{data.filename}' does not exist.")

    if not requested_path.is_file():
        raise ValueError(f"'{data.filename}' is not a file.")

    return requested_path.read_text(encoding="utf-8")

FILE_READER_TOOL = Tool(
    name="file_reader",
    description="Reads the contents of a file, restricted to a sandboxed folder.",
    input_schema=FileReaderInput,
    handler=read_file,
)