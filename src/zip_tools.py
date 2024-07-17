import os
import zipfile


def extract_zip(zip_path: str, extract_to: str) -> None:
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(extract_to)
