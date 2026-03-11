# Copyright 2021-2025 ONDEWO GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import importlib.util
import os
import sys
import tempfile
from collections.abc import Generator
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest
from setuptools import Extension


ROOT: Path = Path(__file__).parent.parent
SETUP_PY_PATH: Path = ROOT / "setup.py"


def _load_setup_module(
    mock_cythonize: MagicMock | None = None,
) -> tuple[ModuleType, MagicMock, MagicMock]:
    """Load setup.py with Cython and setuptools.setup mocked out.

    Returns:
        Tuple of (module, mock_cythonize, mock_setup).
    """
    sys.modules.pop("setup", None)

    if mock_cythonize is None:
        mock_cythonize = MagicMock(return_value=[])

    mock_setup: MagicMock = MagicMock()
    cython_build_mock: MagicMock = MagicMock()
    cython_build_mock.cythonize = mock_cythonize

    with (
        patch.dict(
            "sys.modules",
            {
                "Cython": MagicMock(),
                "Cython.Build": cython_build_mock,
            },
        ),
        patch("setuptools.setup", mock_setup),
    ):
        spec = importlib.util.spec_from_file_location("setup", SETUP_PY_PATH)
        assert spec is not None
        assert spec.loader is not None
        mod: ModuleType = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)  # type: ignore[union-attr]

    sys.modules.pop("setup", None)
    return mod, mock_cythonize, mock_setup


class TestMakeExtensions:
    """Tests for the make_extensions function in setup.py."""

    @pytest.fixture(autouse=True)
    def _cleanup(self) -> Generator[None]:
        """Remove cached setup module before and after each test."""
        sys.modules.pop("setup", None)
        yield
        sys.modules.pop("setup", None)

    def test_empty_directory_returns_empty_list(self) -> None:
        """make_extensions on an empty directory returns an empty list."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert result == []

    def test_return_type_is_list(self) -> None:
        """make_extensions always returns a list."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert isinstance(result, list)

    def test_py_file_creates_one_extension(self) -> None:
        """A single .py file in the directory produces one Extension."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "module.py").write_text("# test")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert len(result) == 1
        assert isinstance(result[0], Extension)

    def test_main_py_at_root_is_excluded(self) -> None:
        """__main__.py at the base directory level is excluded."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "__main__.py").write_text("# main")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert result == []

    def test_main_py_in_subdir_is_excluded(self) -> None:
        """__main__.py in a subdirectory is also excluded."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir: Path = Path(tmpdir, "pkg")
            subdir.mkdir()
            (subdir / "__main__.py").write_text("# sub main")
            (subdir / "other.py").write_text("# other")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert len(result) == 1

    def test_only_main_py_files_returns_empty(self) -> None:
        """Directory containing only __main__.py files returns empty list."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "__main__.py").write_text("# main")
            sub: Path = Path(tmpdir, "sub")
            sub.mkdir()
            (sub / "__main__.py").write_text("# sub main")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert result == []

    def test_module_name_uses_dots_not_path_sep(self) -> None:
        """Extension module names use dots instead of path separators."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            sub: Path = Path(tmpdir, "pkg")
            sub.mkdir()
            (sub / "mod.py").write_text("# mod")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert len(result) == 1
        assert os.sep not in result[0].name

    def test_module_name_has_no_py_suffix(self) -> None:
        """Extension module name must not end with .py."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "mymodule.py").write_text("# test")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert len(result) == 1
        assert not result[0].name.endswith(".py")

    def test_extension_source_is_original_filepath(self) -> None:
        """Each Extension's sources list contains the original .py file path."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file: Path = Path(tmpdir, "module.py")
            py_file.write_text("# test")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert len(result) == 1
        assert str(py_file) in result[0].sources

    def test_extensions_returned_in_sorted_order(self) -> None:
        """Extensions are returned in ascending alphabetical order by filepath."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            for name in ("z_mod.py", "a_mod.py", "m_mod.py"):
                Path(tmpdir, name).write_text("# test")
            result: list[Extension] = mod.make_extensions(tmpdir)
        names: list[str] = [ext.name for ext in result]
        assert names == sorted(names)

    def test_nested_py_files_are_discovered_recursively(self) -> None:
        """Deeply nested .py files are found via recursive glob."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            deep: Path = Path(tmpdir, "a", "b", "c")
            deep.mkdir(parents=True)
            (deep / "deep.py").write_text("# deep")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert len(result) == 1

    def test_multiple_files_across_dirs(self) -> None:
        """make_extensions discovers files across multiple directories."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                Path(tmpdir, f"mod{i}.py").write_text(f"# mod{i}")
            sub: Path = Path(tmpdir, "sub")
            sub.mkdir()
            for i in range(2):
                (sub / f"sub_mod{i}.py").write_text(f"# sub{i}")
            Path(tmpdir, "__main__.py").write_text("# main")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert len(result) == 5  # 3 root + 2 sub; __main__.py excluded

    def test_non_py_files_are_excluded(self) -> None:
        """Non-.py files (.txt, .pyx) are not included in extensions."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "module.txt").write_text("not python")
            Path(tmpdir, "module.pyx").write_text("cython source")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert result == []

    def test_extension_name_derived_from_path_components(self) -> None:
        """Module name is built by replacing path separators with dots."""
        mod, _, _ = _load_setup_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            sub: Path = Path(tmpdir, "pkg", "sub")
            sub.mkdir(parents=True)
            (sub / "leaf.py").write_text("# leaf")
            result: list[Extension] = mod.make_extensions(tmpdir)
        assert len(result) == 1
        # Name contains 'pkg' and 'sub' and 'leaf' joined by dots
        parts: list[str] = result[0].name.split(".")
        assert "pkg" in parts
        assert "sub" in parts
        assert "leaf" in parts


class TestSetupModuleLevel:
    """Tests for the module-level code executed when setup.py is imported."""

    @pytest.fixture(autouse=True)
    def _cleanup(self) -> Generator[None]:
        """Remove cached setup module before and after each test."""
        sys.modules.pop("setup", None)
        yield
        sys.modules.pop("setup", None)

    def test_cythonize_is_called_once_on_import(self) -> None:
        """cythonize() is called exactly once when setup.py is loaded."""
        mock_cythonize: MagicMock = MagicMock(return_value=[])
        _, mock_cyz, _ = _load_setup_module(mock_cythonize)
        mock_cyz.assert_called_once()

    def test_cythonize_receives_language_level_3(self) -> None:
        """cythonize() is called with language_level=3."""
        mock_cythonize: MagicMock = MagicMock(return_value=[])
        _, mock_cyz, _ = _load_setup_module(mock_cythonize)
        _, kwargs = mock_cyz.call_args
        assert kwargs.get("language_level") == 3

    def test_cythonize_receives_nthreads_from_cpu_count(self) -> None:
        """cythonize() is called with nthreads equal to os.cpu_count()."""
        mock_cythonize: MagicMock = MagicMock(return_value=[])
        _, mock_cyz, _ = _load_setup_module(mock_cythonize)
        _, kwargs = mock_cyz.call_args
        assert kwargs.get("nthreads") == os.cpu_count()

    def test_cythonize_first_arg_is_list_of_extensions(self) -> None:
        """cythonize() receives a list (combined extensions) as its first argument."""
        mock_cythonize: MagicMock = MagicMock(return_value=[])
        _, mock_cyz, _ = _load_setup_module(mock_cythonize)
        args, _ = mock_cyz.call_args
        assert isinstance(args[0], list)

    def test_setup_is_called_once_on_import(self) -> None:
        """setuptools.setup() is called exactly once when setup.py is loaded."""
        _, _, mock_setup = _load_setup_module()
        mock_setup.assert_called_once()

    def test_setup_receives_ext_modules_keyword(self) -> None:
        """setup() is called with the ext_modules keyword argument."""
        _, _, mock_setup = _load_setup_module()
        _, kwargs = mock_setup.call_args
        assert "ext_modules" in kwargs

    def test_setup_ext_modules_matches_cythonize_output(self) -> None:
        """The ext_modules passed to setup() is exactly what cythonize() returned."""
        mock_ext: list[MagicMock] = [MagicMock(spec=Extension)]
        mock_cythonize: MagicMock = MagicMock(return_value=mock_ext)
        _, _, mock_setup = _load_setup_module(mock_cythonize)
        _, kwargs = mock_setup.call_args
        assert kwargs["ext_modules"] == mock_ext

    def test_module_exposes_make_extensions_callable(self) -> None:
        """The loaded setup module exposes make_extensions as a callable."""
        mod, _, _ = _load_setup_module()
        assert callable(mod.make_extensions)

    def test_module_exposes_extensions_attribute(self) -> None:
        """The loaded setup module exposes an extensions attribute."""
        mock_ext: list[MagicMock] = [MagicMock(spec=Extension)]
        mock_cythonize: MagicMock = MagicMock(return_value=mock_ext)
        mod, _, _ = _load_setup_module(mock_cythonize)
        assert hasattr(mod, "extensions")
        assert mod.extensions == mock_ext
