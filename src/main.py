import asyncio
import os

import aiohttp

from file_downloader import FileDownloader
from hash_tools import calculate_sha256_hashes_from_directory, save_hashes_to_file
from zip_tools import extract_zip


async def main():

    archive_name = "../archive.zip"
    tmp_folder = "../tmp"
    file_url = "https://gitea.radium.group/radium/project-configuration/archive/master.zip"
    result_file = "../result.txt"

    async with aiohttp.ClientSession() as session:
        file_downloader = FileDownloader(
            session=session,
            number_of_tasks=3,
        )
        await file_downloader.download_file(
            file_url=file_url,
            file_path=archive_name,
        )

    extract_zip(archive_name, tmp_folder)
    file_hashes = calculate_sha256_hashes_from_directory(tmp_folder)
    await save_hashes_to_file(result_file, file_hashes)

    os.remove(archive_name)

    print(f"SHA256 hashes were saved to the file {result_file}")


if __name__ == "__main__":
    asyncio.run(main())
