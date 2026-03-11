import sys
from unittest.mock import patch

import pytest

from ondewo_nlu_webhook_server.server.__main__ import (
    graceful_shutdown,
    main,
    parse_arguments,
)


class TestParseArguments:
    def test_default_values(self) -> None:
        with patch.object(sys, "argv", ["__main__.py"]):
            args = parse_arguments()
            assert args.port == 59001
            assert args.host == "0.0.0.0"

    def test_custom_port(self) -> None:
        with patch.object(sys, "argv", ["__main__.py", "-p", "8080"]):
            args = parse_arguments()
            assert args.port == 8080

    def test_custom_host(self) -> None:
        with patch.object(sys, "argv", ["__main__.py", "-ht", "127.0.0.1"]):
            args = parse_arguments()
            assert args.host == "127.0.0.1"


class TestGracefulShutdown:
    def test_graceful_shutdown_exits(self) -> None:
        with pytest.raises(SystemExit) as exc_info:
            graceful_shutdown(2, None)
        assert exc_info.value.code == 0


class TestMain:
    def test_main_starts_uvicorn(self) -> None:
        with (
            patch.object(sys, "argv", ["__main__.py"]),
            patch("ondewo_nlu_webhook_server.server.__main__.uvicorn.run") as mock_run,
            patch("ondewo_nlu_webhook_server.server.__main__.signal"),
        ):
            main()
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args
            assert call_kwargs.kwargs["port"] == 59001 or call_kwargs[1]["port"] == 59001

    def test_main_handles_parse_failure(self) -> None:
        with (
            patch.object(sys, "argv", ["__main__.py", "--unknown-flag"]),
            patch("ondewo_nlu_webhook_server.server.__main__.uvicorn.run") as mock_run,
            patch("ondewo_nlu_webhook_server.server.__main__.signal"),
        ):
            main()
            mock_run.assert_called_once()

    def test_main_handles_uvicorn_failure(self) -> None:
        with (
            patch.object(sys, "argv", ["__main__.py"]),
            patch(
                "ondewo_nlu_webhook_server.server.__main__.uvicorn.run",
                side_effect=Exception("bind failed"),
            ),
            patch("ondewo_nlu_webhook_server.server.__main__.signal"),
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
