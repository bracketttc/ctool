"""
Tools for dealing with the CMake cache
"""

import configparser
import pathlib

from cachetools import cached


@cached
def get_cache(binary_dir: pathlib.Path) -> configparser.SectionProxy:
    """
    Read the CMake cache from a binary directory
    """

    cache = configparser.ConfigParser(
        delimiters=("="), comment_prefixes=("#", "//"), interpolation=None
    )
    cache.optionxform = lambda option: option.split(":")[0]

    with (binary_dir / "CMakeCache.txt").open("r") as cache_file:
        cache.read_string("[cache]\n" + cache_file.read())

    # Remove internal-use-only special keys
    for key in cache['cache'].keys():
        if key.endswith("-ADVANCED") or key.endswith("-STRINGS"):
            cache.remove_option('cache', key)

    return cache["cache"]
