from abc import ABC
from typing import Any

from grpc import StatusCode


class GRPCException(Exception, ABC):
    CODE: StatusCode = StatusCode.UNKNOWN


class InvalidArgumentException(GRPCException):
    CODE: StatusCode = StatusCode.INVALID_ARGUMENT


class LanguageCodeError(InvalidArgumentException):
    """
    General component language error
    """

    def __init__(self, reason: Any, *args: Any) -> None:
        super(LanguageCodeError, self).__init__(reason, *args)
        self.reason = reason

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}: {self.reason}'

    def __str__(self) -> str:
        return f'{self.__class__.__name__}: {self.reason}'


class NotALanguageError(LanguageCodeError):
    """
    Error: a value was provided which should be of type LanguageCode but is not.
    """
    pass
