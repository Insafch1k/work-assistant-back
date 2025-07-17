import requests
import base64


def download_photo_to_base64(photo_url):
    try:
        response = requests.get(photo_url)
        response.raise_for_status()

        photo_base64 = base64.b64encode(response.content).decode('utf-8')
        return photo_base64
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при загрузке фото: {e}")
        return None
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return None