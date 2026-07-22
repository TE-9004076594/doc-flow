"""File storage service with local filesystem backend and S3 interface stub."""

import os
import shutil
import uuid
from pathlib import Path
from typing import BinaryIO, Optional
from app.core.config import settings


class FileStorage:
    """Local filesystem storage with S3-compatible interface patterns.

    MVP uses local filesystem. V1 can swap implementation for S3/boto3
    without changing the service interface.
    """

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_subdir(self, subdir: str) -> Path:
        """Ensure a subdirectory exists and return its path."""
        path = self.base_dir / subdir
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save(self, subdir: str, filename: str, content: bytes) -> str:
        """Save a file and return its relative path."""
        subdir_path = self._ensure_subdir(subdir)
        # Add UUID prefix to avoid name collisions
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = subdir_path / unique_name
        file_path.write_bytes(content)
        return str(Path(subdir) / unique_name)

    def save_from_stream(self, subdir: str, filename: str, stream: BinaryIO) -> str:
        """Save from a binary stream and return relative path."""
        content = stream.read()
        return self.save(subdir, filename, content)

    def read(self, relative_path: str) -> Optional[bytes]:
        """Read a file by its relative path."""
        full_path = self.base_dir / relative_path
        if full_path.exists() and full_path.is_file():
            return full_path.read_bytes()
        return None

    def delete(self, relative_path: str) -> bool:
        """Delete a file by its relative path."""
        full_path = self.base_dir / relative_path
        if full_path.exists() and full_path.is_file():
            full_path.unlink()
            return True
        return False

    def get_full_path(self, relative_path: str) -> str:
        """Get the absolute filesystem path for a relative path."""
        return str(self.base_dir / relative_path)

    def copy(self, source_rel_path: str, target_subdir: str, new_filename: str) -> str:
        """Copy a file to a new location and return the new relative path."""
        source = self.base_dir / source_rel_path
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source_rel_path}")
        target_dir = self._ensure_subdir(target_subdir)
        dest = target_dir / new_filename
        shutil.copy2(str(source), str(dest))
        return str(Path(target_subdir) / new_filename)


# Singleton instances
template_storage = FileStorage(os.path.join(settings.UPLOAD_DIR, "templates"))
document_storage = FileStorage(os.path.join(settings.OUTPUT_DIR, "documents"))
import_storage = FileStorage(os.path.join(settings.UPLOAD_DIR, "imports"))
