from ondewo_nlu_webhook_server_custom_integration.error_handlers import (
    CustomHttpException,
    handle_internal_error,
)


class TestCustomHttpException:
    def test_creation(self) -> None:
        exc = CustomHttpException(status_code=404, detail="Not found")
        assert exc.status_code == 404
        assert exc.detail == "Not found"


class TestHandleInternalError:
    def test_returns_500_exception(self) -> None:
        original = ValueError("something broke")
        result = handle_internal_error(original)
        assert isinstance(result, CustomHttpException)
        assert result.status_code == 500
        assert result.detail == "An internal error occurred."
