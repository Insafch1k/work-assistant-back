from typing import Optional, TypeVar, Generic, Union, Dict, Any
import inspect
import traceback

from flask import Response, jsonify
from loguru import logger
from pydantic import BaseModel

from project import settings

T = TypeVar('T')


class DataState(BaseModel, Generic[T]):
    data: Optional[T] = None
    error_message: Optional[str] = None
    error_details: Optional[str] = None
    error_code: Optional[int] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None
    show_traceback: bool = False

    def to_response(self) -> (Response, int):

        # Создаем структуру для JSON ответа
        result = {}
        # if self.error_code:
        #     result["code"] = self.error_code

        if self.error_message:
            result["message"] = self.error_message

        if settings.DEBUG_RESPONSE:
            if self.error_type:
                result["type"] = self.error_type

            if self.error_details:
                result["details"] = self.error_details

            if self.traceback and self.show_traceback:
                result["traceback"] = self.traceback

        return  jsonify(result), self.error_code


class DataSuccess(DataState[T]):
    def __init__(self, data: T = None) -> None:
        super().__init__(data=data)

    def __bool__(self):
        return True

    def to_response(self) -> (Response, int):
        return jsonify({"data": self.data}), 200


class DataFailedMessage(DataState):
    def __init__(
            self,
            error_message: Optional[str] = "Unknown error",
            error: Optional[Exception] = None,
            code: int = 500,
            show_traceback: bool = False,
    ):
        """
        Класс для представления неудачного результата операции с данными.

        Args:
            error_message (Optional[str]): Человеко-читаемое сообщение об ошибке.
                Может использоваться самостоятельно или в сочетании с исключением.
                По умолчанию: "Unknown error"

            error (Optional[Exception]): Объект исключения, если ошибка была поймана.
                Если передан, будет извлечен traceback и тип исключения.
                По умолчанию: None

            code (int): HTTP статус-код или кастомный код ошибки.
                Используется для определения типа ошибки в API.
                По умолчанию: 500 (Internal Server Error)

            show_traceback (bool): Флаг, указывающий нужно ли включать traceback
                в JSON ответ.
                По умолчанию: False

        Examples:
            >>> # Простое сообщение об ошибке
            >>> DataFailedMessage(error_message="User not found", code=404)

            >>> # Ошибка с исключением
            >>> try:
            >>>     risky_operation()
            >>> except Exception as e:
            >>>     DataFailedMessage(error_message="Operation failed", error=e)

            >>> # Исключение с принудительным показом traceback
            >>> DataFailedMessage(error=e, show_traceback=True)

            >>> # Комбинированное использование
            >>> DataFailedMessage(
            >>>     error_message="Database connection failed",
            >>>     error=connection_error,
            >>>     code=503,
            >>>     show_traceback=True
            >>> )

        Notes:
            - При передаче и error_message и error, сообщения будут объединены
            - Traceback логируется всегда, но в JSON ответ включается только
              при show_traceback=True или в режиме разработки
            - Код ошибки используется для установки HTTP статуса в ответе API
        """
        error_type = None
        tb_str = None
        error_details = None

        if error is not None:
            error_type = type(error).__name__
            tb_str = traceback.format_exc()
            error_details = f"{error_type}: {str(error)}"

        # Логируем с информацией о местоположении
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back
            caller_info = inspect.getframeinfo(caller_frame)

            file_name = caller_info.filename
            function_name = caller_info.function
            line_number = caller_info.lineno

            full_log_message = f"{error_message}\nDetails: {error_details}"
            if tb_str and tb_str != "NoneType: None\n":
                full_log_message += f"\n{tb_str}"

            logger.opt(depth=1).error(full_log_message)

            # Сохраняем данные
            super().__init__(
                error_message=error_message,
                error_code=code,
                error_type=error_type,
                traceback=tb_str if tb_str and tb_str != "NoneType: None\n" else None,
                show_traceback=show_traceback,
                error_details=error_details
            )

        finally:
            del frame
            if 'caller_frame' in locals():
                del caller_frame


    def __bool__(self):
        return False