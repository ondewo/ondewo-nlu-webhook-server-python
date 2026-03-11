from grpc import StatusCode

from ondewo_nlu_webhook_server.custom_exceptions import (
    GRPCException,
    InvalidArgumentException,
    LanguageCodeError,
    NotALanguageError,
)


class TestCustomExceptions:
    def test_language_code_error(self) -> None:
        err = LanguageCodeError("test reason")
        assert err.reason == "test reason"
        assert "test reason" in repr(err)
        assert "test reason" in str(err)

    def test_not_a_language_error(self) -> None:
        err = NotALanguageError("bad value")
        assert isinstance(err, LanguageCodeError)
        assert isinstance(err, InvalidArgumentException)
        assert err.reason == "bad value"

    def test_grpc_exception_code(self) -> None:
        assert GRPCException.CODE == StatusCode.UNKNOWN
        assert InvalidArgumentException.CODE == StatusCode.INVALID_ARGUMENT
