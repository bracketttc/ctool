"""
ctool
"""

from difflib import get_close_matches
from shutil import which
import glob
import os
import subprocess
import sys

from .util import remove_prefix


def find_commands():
    """
    Discover all ctool commands available
    """
    try:
        paths = os.environ["PATH"].split(os.pathsep)
    except KeyError:
        paths = os.defpath.split(os.pathsep)
    paths = list(set(paths))

    results = []
    for path_dir in paths:
        results += glob.glob(os.path.join(glob.escape(path_dir), "ctool-*"))

    commands = [
        remove_prefix(os.path.basename(result), "ctool-")
        for result in results
        if os.access(result, os.X_OK | os.R_OK)
    ]

    return commands


def print_usage():
    """
    Print ctool usage
    """
    print(
        "usage: ctool <command> [OPTIONS]\n"
        "\n"
        "Known commands:\n"
        "   changed-tests\tList or run tests changed by a set of files\n"
        "   depends\t\tList or install project dependencies\n"
    )


def main():
    """
    ctool entry-point
    """
    if len(sys.argv) == 1:
        print_usage()
        return 0

    command = sys.argv[1]
    command_exec = which("ctool-" + command)
    if command_exec is None:
        print(f"ctool: `{command}` is not an available ctool command.")

        alternate_command = get_close_matches(command, find_commands(), n=1, cutoff=0.7)
        for cmd in alternate_command:
            print(f"\nMaybe you meant: `ctool {cmd}`?")
        return 1

    with subprocess.Popen([command_exec] + sys.argv[2:]) as proc:
        proc.wait()
        return proc.returncode
