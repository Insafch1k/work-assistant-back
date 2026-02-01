import os
from pathlib import Path

from flask import Blueprint, jsonify, request, send_from_directory
from loguru import logger

media_router = Blueprint("media_router", __name__)
media_root = Path(os.environ.get('MEDIA_ROOT'))

@media_router.route('/avatars/<path:filename>')
def serve_media(filename):
    return send_from_directory(media_root / "avatars", filename)