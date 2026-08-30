import pytest

from app.tools.file_reader import FileReaderInput, read_file, SANDBOX_DIR

def test_can_read_a_file_inside_the_sandbox():
    result = read_file(FileReaderInput(filename="hello.txt"))
    assert "Hello" in result

def test_reading_a_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        read_file(FileReaderInput(filename="does_not_exist.txt"))

def test_cannot_escape_the_sandbox_with_dot_dot():
    with pytest.raises(PermissionError):
        read_file(FileReaderInput(filename="../requirements.txt"))

def test_cannot_read_an_absolute_path_outside_sandbox():
    with pytest.raises(PermissionError):
        read_file(FileReaderInput(filename="/etc/passwd"))

def test_cannot_read_a_directory_as_a_file():
    with pytest.raises((PermissionError, ValueError, FileNotFoundError)):
        read_file(FileReaderInput(filename="."))