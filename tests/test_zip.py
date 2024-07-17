import os
import zipfile

import pytest

from src.zip_tools import extract_zip


@pytest.fixture
def zip_file(tmp_path):
    zip_path = tmp_path / "test.zip"
    with zipfile.ZipFile(zip_path, "w") as zip:
        zip.writestr("test_1.txt", "This is a test txt file")
        zip.writestr("test_2.txt", "This is another test txt file")
    return zip_path


def test_extract_zip_creates_directory(tmp_path, zip_file):
    extract_to = tmp_path / "extracted"
    extract_zip(zip_file, extract_to)
    assert os.path.isdir(extract_to)


def test_extract_zip_extracts_all_files(tmp_path, zip_file):
    extract_to = tmp_path / "extracted"
    extract_zip(zip_file, extract_to)
    assert os.path.isfile(extract_to / "test_1.txt")
    assert os.path.isfile(extract_to / "test_2.txt")


def test_extract_zip_handles_nonexistent_zip(tmp_path):
    extract_to = tmp_path / "extracted"
    with pytest.raises(FileNotFoundError):
        extract_zip("aaaaa.zip", extract_to)
