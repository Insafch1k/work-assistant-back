import os
import uuid
import requests
from typing import Optional
from flask import request, current_app
from project.utils.logger import Logger

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def save_image(
        save_dir: str,
        url: Optional[str] = None,
        default_ext: str = ".jpg"
) -> Optional[str]:
    """Сохраняет изображение из URL."""
    if not url:
        raise ValueError("Должен быть указан url фотографии")

    try:
        os.makedirs(os.path.join('photos', save_dir), exist_ok=True)
        filename = str(uuid.uuid4())
        filepath = os.path.join('photos', save_dir, filename)

        with requests.get(url, stream=True) as response:
            response.raise_for_status()

            ext = os.path.splitext(url.split('?')[0])[1].lower()
            if not ext or f".{ext}" not in ALLOWED_EXTENSIONS:
                content_type = response.headers.get('content-type', '').split(';')[0]
                ext_mapping = {
                    'image/jpeg': '.jpg',
                    'image/png': '.png',
                    'image/gif': '.gif',
                    'image/webp': '.webp'
                }
                ext = ext_mapping.get(content_type, default_ext)

            filepath += ext

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024 * 8):  # Увеличенный буфер
                    if chunk:  # Фильтр keep-alive chunks
                        f.write(chunk)

        print(os.path.join(save_dir, f"{filename}{ext}"))
        return os.path.join(save_dir, f"{filename}{ext}")

    except Exception as e:
        print(f"Ошибка при сохранении изображения: {str(e)}")
        return None


def photo_url_convert(data):
    photo_url = None
    if data:  # Проверяем наличие фото (поле photo в запросе)
        clean_path = data.replace('\\', '/').lstrip('/')

        # Формируем полный URL (учитываем, что photos лежит на уровне с project)
        base_url = request.host_url.rstrip('/')
        photo_url = f"{base_url}/api/photos/{clean_path}"

        # Для тестирования можно добавить проверку существования файла
        if current_app.config.get('DEBUG'):
            full_path = os.path.join(
                os.path.dirname(current_app.root_path),  # Поднимаемся на уровень выше
                'photos',
                clean_path)
            if not os.path.exists(full_path):
                Logger.warning(f"Dev warning: Photo file missing at {full_path}")

    return photo_url
