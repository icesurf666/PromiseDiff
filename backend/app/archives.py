from __future__ import annotations

from io import BytesIO
from pathlib import PurePosixPath
from zipfile import BadZipFile, ZipFile

MAX_FILES = 8
MAX_DECOMPRESSED = 60 * 1024 * 1024
MAX_RATIO = 100


class ArchiveError(ValueError):
    pass


def unpack_pdfs(payload: bytes) -> list[tuple[str, bytes]]:
    try:
        archive = ZipFile(BytesIO(payload))
    except BadZipFile as exc:
        raise ArchiveError("Invalid ZIP archive") from exc
    with archive:
        entries = archive.infolist()
        if len(entries) > MAX_FILES:
            raise ArchiveError("Archive contains too many files")
        names: set[str] = set()
        declared = 0
        result = []
        for entry in entries:
            path = PurePosixPath(entry.filename)
            normalized = str(path)
            unsafe = path.is_absolute() or ".." in path.parts or entry.is_dir()
            symlink = (entry.external_attr >> 16) & 0o170000 == 0o120000
            ratio = entry.file_size / max(entry.compress_size, 1)
            if unsafe or symlink or normalized in names:
                raise ArchiveError("Archive contains an unsafe or duplicate path")
            if entry.flag_bits & 1 or entry.filename.lower().endswith(".zip"):
                raise ArchiveError("Encrypted or nested archives are not supported")
            if path.suffix.lower() != ".pdf":
                raise ArchiveError("ZIP archives may contain PDF files only")
            if ratio > MAX_RATIO or declared + entry.file_size > MAX_DECOMPRESSED:
                raise ArchiveError("Archive decompression limit exceeded")
            names.add(normalized)
            declared += entry.file_size
            with archive.open(entry) as member:
                data = member.read(MAX_DECOMPRESSED + 1)
            if len(data) != entry.file_size or len(data) > MAX_DECOMPRESSED:
                raise ArchiveError("Archive member size is invalid")
            result.append((path.name, data))
    if not result:
        raise ArchiveError("Archive contains no PDFs")
    return result
