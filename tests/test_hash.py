import os
import hashlib

import aiofiles
import pytest

from src.hash_tools import (
    FileHash,
    calculate_sha256,
    calculate_sha256_hashes_from_directory,
    save_hashes_to_file,
)


def test_calculate_sha256():
    data = b"radium"
    expected_hash = hashlib.sha256(data).hexdigest()
    assert calculate_sha256(data) == expected_hash


@pytest.fixture
def mock_directory(tmp_path):
    dir_path = tmp_path / "test_dir"
    os.makedirs(dir_path)
    file_1 = dir_path / "file_1.txt"
    file_2 = dir_path / "file_2.txt"
    file_1.write_text("content of file_1.txt")
    file_2.write_text("content of file_2.txt")
    return dir_path


def test_calculate_sha256_hashes_from_directory(mock_directory):
    hashes = calculate_sha256_hashes_from_directory(mock_directory)
    expected_hashes = [
        FileHash(
            file_name=str(mock_directory / "file_1.txt"),
            hash=hashlib.sha256(b"content of file_1.txt").hexdigest()
        ),
        FileHash(
            file_name=str(mock_directory / "file_2.txt"),
            hash=hashlib.sha256(b"content of file_2.txt").hexdigest()
        )
    ]
    assert hashes == expected_hashes


@pytest.mark.asyncio
async def test_save_hashes_to_file(tmp_path):
    output_file = tmp_path / "hashes.txt"
    file_hashes = [
        FileHash(file_name="file_1.txt", hash="hash1"),
        FileHash(file_name="file_2.txt", hash="hash2")
    ]
    await save_hashes_to_file(output_file, file_hashes)
    async with aiofiles.open(output_file, "r") as file:
        content = await file.read()
    expected_content = "file_1.txt:\thash1\nfile_2.txt:\thash2\n"
    assert content == expected_content
