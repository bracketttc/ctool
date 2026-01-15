"""
ctool utility functions
"""

import configparser
import functools
import pathlib
from typing import Callable, Optional


def reverse_walk(
    predicate: Callable[[pathlib.Path], bool], start_path: Optional[pathlib.Path] = None
) -> Optional[pathlib.Path]:
    """
    Walk up the directory tree until root or predicate evaluates to True
    """

    eval_path = start_path if start_path is not None else pathlib.Path.cwd()
    while eval_path != eval_path.anchor:
        if predicate(eval_path):
            return eval_path
        eval_path = eval_path.parent
    return None


def find_binary_dir(path: Optional[pathlib.Path] = None) -> Optional[pathlib.Path]:
    """
    Search backward for a binary directory.
    """

    binary_dir = reverse_walk(is_binary_dir, path)
    if binary_dir is not None:
        return binary_dir

    source_dir = find_source_dir(path)
    if source_dir is not None:
        if (source_dir / ".ctoolrc").exists():
            pass

    return None


def is_source_dir(path: Optional[pathlib.Path] = None) -> bool:
    """
    Determines if argument path (or cwd) is a CMake source directory
    """
    check_path = path if path is not None else pathlib.Path.cwd()
    return (check_path / "CMakeLists.txt").exists()


def find_source_dir(path: Optional[pathlib.Path] = None) -> Optional[pathlib.Path]:
    """
    Search backward for a CMake project root.
    """

    if is_binary_dir(path):
        return get_source_dir(path)

    return reverse_walk(is_source_dir, path)


def is_binary_dir(path: Optional[pathlib.Path] = None) -> bool:
    """
    Determines if argument path (or cwd) is a binary directory
    """

    check_path = path if path is not None else pathlib.Path.cwd()
    cache_file = check_path / "CMakeCache.txt"
    cmake_files_dir = check_path / "CMakeFiles"

    return cache_file.is_file() and cmake_files_dir.is_dir()


@functools.lru_cache
def read_cache(path: Optional[pathlib.Path] = None) -> configparser.SectionProxy:
    """
    Read CMake cache into memory
    """

    parser = configparser.ConfigParser(
        allow_no_value=True, comment_prefixes=("#", "//"), delimiters=("=")
    )

    # tell parser to strip type hints from key names
    def discard_type(optionstr: str) -> str:
        return optionstr.split(":")[0]

    setattr(parser, "optionxform", discard_type)

    # Read CMakeCache.txt
    path = path if path is not None else pathlib.Path.cwd()
    cache_path = path / "CMakeCache.txt"
    # `configparser` requires all values be within a section heading, and it's the best fit
    # otherwise, so we give it a fake section heading to make it happy.
    with cache_path.open("r", encoding="utf-8") as f:
        cache_str = "[cache]\n" + f.read()
    parser.read_string(cache_str)

    # Remove the advanced property markers
    remove_keys = [key for key in parser["cache"].keys() if key.endswith("-ADVANCED")]
    for key in remove_keys:
        parser.remove_option("cache", key)

    # Return just the section that we put all the cache entries in
    return parser["cache"]


def get_cache_value(key: str, path: Optional[pathlib.Path] = None):
    """
    Retrieve a value from the CMake cache.
    Returns None if the value is not set.
    """
    return read_cache(path)[key]


def get_source_dir(path: Optional[pathlib.Path] = None) -> Optional[pathlib.Path]:
    """
    Returns the source directory as recorded in the CMake cache.
    """

    if not is_binary_dir(path):
        return None

    project_name = get_cache_value("CMAKE_PROJECT_NAME", path)
    return get_cache_value(f"{project_name}_SOURCE_DIR", path)
