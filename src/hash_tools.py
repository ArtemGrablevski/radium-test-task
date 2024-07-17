import hashlib
import os
from dataclasses import dataclass

import aiofiles


@dataclass(frozen=True, slots=True)
class FileHash:
    file_name: str
    hash: str


def calculate_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def calculate_sha256_hashes_from_directory(directory: str) -> list[FileHash]:
    hashes = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as read_file:
                file_hash = calculate_sha256(read_file.read())
            hashes.append(
                FileHash(
                    file_name=file_path,
                    hash=file_hash,
                ),
            )
    return hashes


async def save_hashes_to_file(output_file: str, file_hashes: list[FileHash]) -> None:
    async with aiofiles.open(output_file, "w") as file:
        for file_hash in file_hashes:
            await file.write(f"{file_hash.file_name}:\t{file_hash.hash}\n")
