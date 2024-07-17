import asyncio

import aiofiles
import aiohttp


class FileDownloaderError(Exception):
    ...


class FileDownloader:

    def __init__(self, session: aiohttp.ClientSession, number_of_tasks: int) -> None:
        self.number_of_tasks = number_of_tasks
        self.session = session

    async def download_file(self, file_url: str, file_path: str) -> None:
        file_size = await self._get_file_size(file_url)
        chunk_size = file_size // self.number_of_tasks
        tasks = []
        for task_number in range(self.number_of_tasks):
            start = task_number * chunk_size
            end = start + chunk_size - 1 if task_number < self.number_of_tasks - 1 else file_size - 1
            tasks.append(self._fetch_chunk(file_url, start, end))
        chunks = await asyncio.gather(*tasks)
        await self._combine_chunks(file_path, chunks)

    async def _fetch_chunk(self, file_url: str, start: int, end: int) -> bytes:
        headers = {
            "Range": f"bytes={start}-{end}",
        }
        async with self.session.get(file_url, headers=headers) as response:
            if response.status != 206:
                raise FileDownloaderError(f"Failed to fetch chunk, status code: {response.status}")
            return await response.content.read()

    async def _combine_chunks(self, file_path: str, chunks: list[bytes]) -> None:
        async with aiofiles.open(file_path, "wb") as file:
            for chunk in chunks:
                await file.write(chunk)

    async def _get_file_size(self, file_url: str) -> int:
        async with self.session.head(file_url) as response:
            if response.status != 200:
                raise FileDownloaderError(f"Failed to get file size, status code: {response.status}")
            return int(response.headers["Content-Length"])
