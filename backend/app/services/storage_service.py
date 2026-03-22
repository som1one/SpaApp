import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parents[2]


class StorageService:
    @staticmethod
    def _base_path() -> Path:
        base_path = Path(settings.UPLOAD_DIR)
        if not base_path.is_absolute():
            base_path = BASE_DIR / base_path
        base_path.mkdir(parents=True, exist_ok=True)
        return base_path

    @staticmethod
    def save_menu_image(file: UploadFile) -> str:
        upload_dir = StorageService._base_path() / "menu"
        upload_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(file.filename or "").suffix.lower()
        filename = f"{uuid4().hex}{suffix or '.jpg'}"
        file_path = upload_dir / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        relative_path = Path("uploads") / "menu" / filename
        return "/" + relative_path.as_posix()

    @staticmethod
    def save_avatar_image(file: UploadFile) -> str:
        upload_dir = StorageService._base_path() / "avatars"
        upload_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(file.filename or "").suffix.lower()
        filename = f"{uuid4().hex}{suffix or '.jpg'}"
        file_path = upload_dir / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        relative_path = Path("uploads") / "avatars" / filename
        return "/" + relative_path.as_posix()

    @staticmethod
    def save_custom_content_image(file: UploadFile) -> str:
        upload_dir = StorageService._base_path() / "custom-content"
        upload_dir.mkdir(parents=True, exist_ok=True)

        suffix = Path(file.filename or "").suffix.lower()
        filename = f"{uuid4().hex}{suffix or '.jpg'}"
        file_path = upload_dir / filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        relative_path = Path("uploads") / "custom-content" / filename
        return "/" + relative_path.as_posix()

