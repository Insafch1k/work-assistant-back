from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask_socketio import emit, disconnect


def require_jwt_or_disconnect():
    """
    Проверяем JWT (подпись, exp) через flask_jwt_extended прямо из текущего request.
    Токен ожидается либо в заголовке Authorization, либо в query (?token=...).
    Возвращает user_id (identity). В случае проблемы отправляет 'error' и disconnect().
    """
    try:
        # Ограничим места поиска только query в сокетах — это надёжнее для браузера.
        # Но так как в app.config включены и headers, и query_string, тут явно укажем.
        verify_jwt_in_request(locations=["query_string", "headers"])
        uid = get_jwt_identity()
        if uid is None:
            emit("error", {"code": "no_identity"}, namespace="/ws")
            disconnect()
            return ""
        return uid
    except Exception as e:
        # Можно различать типы ошибок по сообщению/классу, но для краткости обобщим
        err = str(e)
        code = "token_expired" if "expired" in err.lower() else "bad_token"
        emit("error", {"code": code}, namespace="/ws")
        disconnect()
        return ""