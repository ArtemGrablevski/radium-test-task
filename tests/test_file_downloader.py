from unittest.mock import patch

from aiohttp import ClientSession
from aioresponses import aioresponses
import pytest

from src.file_downloader import FileDownloader, FileDownloaderError


@pytest.mark.asyncio
async def test_get_file_size():
    async with ClientSession() as session:
        file_downloader = FileDownloader(session, 4)
        with aioresponses() as mock_response:
            mock_response.head("https://radium.com/testfile", headers={"Content-Length": "1000"}, status=200)
            file_size = await file_downloader._get_file_size("https://radium.com/testfile")
            assert file_size == 1000


@pytest.mark.asyncio
async def test_get_file_size_error():
    async with ClientSession() as session:
        file_downloader = FileDownloader(session, 4)
        with aioresponses() as m:
            m.head("https://example.com/testfile", status=404)
            with pytest.raises(FileDownloaderError, match="Failed to get file size, status code: 404"):
                await file_downloader._get_file_size("https://example.com/testfile")


@pytest.mark.asyncio
async def test_fetch_chunk():
    async with ClientSession() as session:
        file_downloader = FileDownloader(session, 4)
        with aioresponses() as mock_response:
            mock_response.get("https://radium.com/testfile", body=b"testdata", status=206)
            chunk = await file_downloader._fetch_chunk("https://radium.com/testfile", 0, 7)
            assert chunk == b"testdata"


@pytest.mark.asyncio
async def test_fetch_chunk_error():
    async with ClientSession() as session:
        file_downloader = FileDownloader(session, 4)
        with aioresponses() as mock_response:
            mock_response.get("https://radium.com/testfile", status=404)
            with pytest.raises(FileDownloaderError, match="Failed to fetch chunk, status code: 404"):
                await file_downloader._fetch_chunk("https://radium.com/testfile", 0, 7)


async def mock_combine_chunks(self, file_path: str, chunks: list[bytes]) -> None:
    assert chunks == [b"chunk1", b"chunk2", b"chunk3", b"chunk4"]


@pytest.mark.asyncio
async def test_download_file():
    async with ClientSession() as session:
        file_downloader = FileDownloader(session, 4)
        with aioresponses() as mock_response:
            mock_response.head("https://radium.com/testfile", headers={"Content-Length": "16"}, status=200)
            mock_response.get("https://radium.com/testfile", body=b"chunk1", status=206)
            mock_response.get("https://radium.com/testfile", body=b"chunk2", status=206)
            mock_response.get("https://radium.com/testfile", body=b"chunk3", status=206)
            mock_response.get("https://radium.com/testfile", body=b"chunk4", status=206)

            with patch.object(FileDownloader, "_combine_chunks", new=mock_combine_chunks):
                await file_downloader.download_file("https://radium.com/testfile", "/tmp/testfile")
