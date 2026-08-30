import pytest
from app.tools.csv_reader import CSVReaderInput, read_csv, CSV_READER_TOOL

def test_reads_all_rows_when_no_filter_given():
    rows = read_csv(CSVReaderInput(filename="people.csv"))
    assert len(rows) == 3
    assert rows[0]["name"] == "Ali"

def test_filters_rows_by_column_value():
    rows = read_csv(
        CSVReaderInput(filename="people.csv", filter_column="city", filter_value="Lahore")
    )
    names = {row["name"] for row in rows}
    assert names == {"Ali", "Zain"}

def test_filter_with_no_matches_returns_empty_list():
    rows = read_csv(
        CSVReaderInput(filename="people.csv", filter_column="city", filter_value="Islamabad")
    )
    assert rows == []

def test_filtering_by_unknown_column_raises_error():
    with pytest.raises(ValueError):
        read_csv(
            CSVReaderInput(filename="people.csv", filter_column="country", filter_value="PK")
        )

def test_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        read_csv(CSVReaderInput(filename="does_not_exist.csv"))

def test_cannot_escape_the_sandbox():
    with pytest.raises(PermissionError):
        read_csv(CSVReaderInput(filename="../requirements.txt"))

def test_tool_metadata_is_correct():
    assert CSV_READER_TOOL.name == "csv_reader"
    assert CSV_READER_TOOL.input_schema is CSVReaderInput