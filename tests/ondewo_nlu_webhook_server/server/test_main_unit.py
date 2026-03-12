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

    def test_main_env_print_exception_is_handled(self) -> None:
        """Cover lines 128-129: exception in the first env-variable print block."""
        original_sorted = sorted

        call_count = 0

        def sorted_raising_on_first_call(iterable, **kwargs):  # type: ignore[no-untyped-def]
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("env sort error")
            return original_sorted(iterable, **kwargs)

        with (
            patch.object(sys, "argv", ["__main__.py"]),
            patch("builtins.sorted", side_effect=sorted_raising_on_first_call),
            patch("ondewo_nlu_webhook_server.server.__main__.uvicorn.run") as mock_run,
            patch("ondewo_nlu_webhook_server.server.__main__.signal"),
        ):
            main()
            mock_run.assert_called_once()

    def test_main_env_log_exception_is_handled(self) -> None:
        """Cover lines 148-149: exception in the second env-variable log block."""
        original_sorted = sorted

        call_count = 0

        def sorted_raising_on_second_call(iterable, **kwargs):  # type: ignore[no-untyped-def]
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                raise Exception("env log sort error")
            return original_sorted(iterable, **kwargs)

        with (
            patch.object(sys, "argv", ["__main__.py"]),
            patch("builtins.sorted", side_effect=sorted_raising_on_second_call),
            patch("ondewo_nlu_webhook_server.server.__main__.uvicorn.run") as mock_run,
            patch("ondewo_nlu_webhook_server.server.__main__.signal"),
        ):
            main()
            mock_run.assert_called_once()

    def test_parse_arguments_long_host_flag(self) -> None:
        """Test that the long --host flag works in parse_arguments."""
        with patch.object(sys, "argv", ["__main__.py", "--host", "192.168.1.1"]):
            args = parse_arguments()
            assert args.host == "192.168.1.1"

    def test_main_workers_from_environment(self) -> None:
        """Test that the number of workers is read from the environment variable."""
        with (
            patch.object(sys, "argv", ["__main__.py"]),
            patch("ondewo_nlu_webhook_server.server.__main__.uvicorn.run") as mock_run,
            patch("ondewo_nlu_webhook_server.server.__main__.signal"),
            patch.dict(
                "os.environ",
                {"ONDEWO_NLU_WEBHOOK_SERVER_PYTHON_NR_OF_WORKERS": "4"},
            ),
        ):
            main()
            mock_run.assert_called_once()
            call_kwargs = mock_run.call_args
            assert call_kwargs.kwargs["workers"] == 4
