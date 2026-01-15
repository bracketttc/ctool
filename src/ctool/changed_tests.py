"""
ctool changed-tests command and related functions
"""

import argparse
import enum
import json
import os
import subprocess
import sys

import git

from .file_api import check_for_reply, request_codemodel
from .util import is_binary_dir


class ChangeType(enum.Enum):
    """
    Represents what kind of change expression is provided to the --changed-by argument.
    """

    GIT = 1
    FILE = 2
    FILELIST = 3
    UNKNOWN = 4


class ChangedByAction(argparse.Action):
    """ """

    def detect_change_type(self, change_expr):
        """
        Determines what kind of change expression is given.
        """

        if change_expr.startswith("git:"):
            return ChangeType.GIT
        if change_expr.startswith("file:"):
            return ChangeType.FILE
        if change_expr.startswith("filelist:"):
            return ChangeType.FILELIST

        if os.path.isfile(change_expr):
            # check if file contains a list of other files
            pass

        return ChangeType.UNKNOWN

    def git_changed_files(self, change_expr):
        """
        Process git change expression into a file list
        """

        change_expr = change_expr.removeprefix("git:")

        repo = git.Repo(os.getcwd(), search_parent_directories=True)
        try:
            return repo.git.diff("--name-only", change_expr, "--")
        except git.exc.GitCommandError as e:
            print(e.stderr.strip().removeprefix("stderr: "))
            sys.exit(e.status)

    def list_changed_files(self, change_type, change_expr):
        """ """

        if change_type == ChangeType.GIT:
            return self.git_changed_files(change_expr)
        if change_type == ChangeType.FILE:
            return []
        if change_type == ChangeType.FILELIST:
            with open(change_expr, "r") as list_source:
                return list_source.readlines()
        return []

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Process the `--changed-by` argument.
        """

        change_type = self.detect_change_type(values)
        fileset = self.list_changed_files(change_type, values)

        regex_expr = (
            fileset  # TODO translate files to tests and then to a -R expression
        )

        # Push our synthesized arguments onto the pass-through arguments to ctest
        vars(namespace).setdefault(argparse._UNRECOGNIZED_ARGS_ATTR, [])
        getattr(namespace, argparse._UNRECOGNIZED_ARGS_ATTR).extend(regex_expr)


def main():
    """
    Entry point for ctool test.
    """

    parser = argparse.ArgumentParser("ctool changed-tests", description="", epilog="")
    parser.add_argument(
        "--changed-by",
        action="store",
        help="",
        metavar="CHANGE EXPR",
    )
    parser.add_argument("--rerun-failed", action="store_true", help="")

    # if no changed-by argument, go by timestamp of last test log

    _, passthru_args = parser.parse_known_intermixed_args()

    if not is_binary_dir():
        print("Not in a CMake binary directory, exiting...")
        sys.exit(1)

    # get JSON description from ctest
    proc = subprocess.run(
        ["/usr/bin/ctest", ".", "--show-only=json-v1"], check=True, capture_output=True
    )
    test_info = json.loads(proc.stdout)
    if "tests" not in test_info or len(test_info["tests"]) == 0:
        print("No tests were found!!!")
        sys.exit(0)

    # check for file-api reply
    if not check_for_reply():
        # make a request
        request_codemodel()

    # read in file-api data

    # combine the two data sources

    # Determine which tests are potentially impacted by the changed files

    # Run ctest
    return subprocess.run(
        ["/usr/bin/ctest", "."] + passthru_args, check=False
    ).returncode
