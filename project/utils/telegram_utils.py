import hashlib
import hmac

def validate_telegram_data(data: dict, bot_token: str) -> bool:
    """Проверяет, что данные действительно от Telegram."""
    hash_str = data.pop("hash")
    data_str = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(bot_token.encode()).digest()
    computed_hash = hmac.new(secret_key, data_str.encode(), hashlib.sha256).hexdigest()
    return computed_hash == hash_str