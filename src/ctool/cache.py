"""
Tools for dealing with the CMake cache
"""

import configparser
import pathlib

from cachetools import cached


@cached(cache={})
def get_cache(binary_dir: pathlib.Path) -> configparser.SectionProxy:
    """
    Read the CMake cache from a binary directory
    """

    cmake_cache = configparser.ConfigParser(
        delimiters=("="), comment_prefixes=("#", "//"), interpolation=None
    )
    # Strip off the CMake variable types from the names
    cmake_cache.optionxform = lambda optionstr: optionstr.split(":")[0]  # type: ignore

    # Prefix CMakeCache.txt with a heading to make it parsable by configparser
    with (binary_dir / "CMakeCache.txt").open("r") as cache_file:
        cmake_cache.read_string("[cache]\n" + cache_file.read())

    # Remove internal-use-only special keys
    for key in cmake_cache["cache"].keys():
        if key.endswith("-ADVANCED") or key.endswith("-STRINGS"):
            cmake_cache.remove_option("cache", key)

    # Return the CMake cache (without exposing our fake section heading)
    return cmake_cache["cache"]
