from typing import Optional, TypeVar, Generic

from loguru import logger
from pydantic import BaseModel

T = TypeVar('T')

class DataState(BaseModel, Generic[T]):
    data: Optional[T]=None
    error_message: Optional[str]=None


class DataSuccess(DataState):
    def __init__(self, data: T=None) -> None:
        super().__init__(data=data)

    def __bool__(self):
        return True


class DataFailedMessage(DataState):
    def __init__(self, error_message: str='') -> None:
        logger.error(error_message)
        super().__init__(error_message=error_message)

    def __bool__(self):
        return False

