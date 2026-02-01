import os
import uuid
from pathlib import Path
from urllib.parse import urlparse

import requests
from PIL import Image, UnidentifiedImageError
from flask import Flask, request, jsonify

app = Flask(__name__)

MEDIA_ROOT = os.environ.get("MEDIA_ROOT", "/media")
AVATAR_DIR = Path(MEDIA_ROOT) / "avatars"

MAX_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP", "SVG"}

def _safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return

def delete_avatar(photo_path: str | None) -> None:
    if not photo_path:
        return
    abs_path = Path(photo_path)
    abs_path = abs_path.resolve()
    _safe_unlink(abs_path)

def save_avatar(img: Image.Image, size: int = 256) -> str:
    # квадратный crop + resize
    img = img.convert("RGBA")
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    img = img.resize((size, size), Image.Resampling.LANCZOS)

    #AVATAR_DIR.mkdir( exist_ok=True)

    filename = f"{uuid.uuid4().hex}.webp"
    abs_path = AVATAR_DIR / filename

    img.save(abs_path, format="WEBP", quality=85, method=6)

    return f"avatars/{filename}"

def load_and_validate_pillow_image(fileobj) -> Image.Image:
    try:
        img = Image.open(fileobj)
        img.load()  # принудительно декодировать сейчас
    except UnidentifiedImageError:
        raise ValueError("File is not a valid image")

    # строгая проверка формата, а не mimetype/расширения
    if img.format not in ALLOWED_FORMATS:
        raise ValueError(f"Unsupported image format: {img.format}")

    return img

def download_image_bytes(url: str, max_bytes: int = MAX_BYTES) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only http/https urls are allowed")
    if not ("telegram" in parsed.hostname or "t.me" in parsed.hostname):
        raise ValueError("URL host is not allowed")

    # stream=True чтобы контролировать размер
    with requests.get(url, stream=True, timeout=(3.05, 10)) as r:
        r.raise_for_status()
        ctype = (r.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        if ctype and ctype not in {"image/jpeg", "image/png", "image/webp", "image/svg"}:
            raise ValueError(f"Remote content-type not allowed: {ctype}")

        data = bytearray()
        for chunk in r.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            data.extend(chunk)
            if len(data) > max_bytes:
                raise ValueError("Remote file too large")
        return bytes(data)