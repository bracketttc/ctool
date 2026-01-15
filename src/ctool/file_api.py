"""
Functions for dealing with cmake-file-api
"""

import json
import os
import pathlib
import subprocess
import sys
from typing import Optional

FILE_API_ROOT = ".cmake/api/v1"
QUERY_DIR = os.path.join(FILE_API_ROOT, "query/client-ctool")
REPLY_DIR = os.path.join(FILE_API_ROOT, "reply")


def request_codemodel(binary_dir=os.getcwd()):
    """
    Make a client statelesss query to the cmake-file-api.
    """

    reconfig = False

    query_dir = os.path.join(binary_dir, QUERY_DIR)
    if not os.path.isdir(query_dir):
        reconfig = True
        try:
            os.makedirs(query_dir)
        except FileExistsError:
            pass

    query_file = os.path.join(query_dir, "codemodel-v2")
    if not os.path.isfile(query_file):
        reconfig = True
        with open(query_file, "w", encoding="utf-8") as _:
            pass

    if not check_for_reply(binary_dir):
        reconfig = True

    if reconfig:
        # TODO Should use the CMake command found in the cache!
        proc = subprocess.run(["/usr/bin/cmake", binary_dir], check=False)
        if proc.returncode != 0:
            sys.exit(proc.returncode)


def get_reply_index(binary_dir: str = os.getcwd()) -> Optional[pathlib.Path]:
    """ """
    # https://cmake.org/cmake/help/latest/manual/cmake-file-api.7.html#v1-reply-index-file
    index_files = sorted(
        pathlib.Path(os.path.join(binary_dir, REPLY_DIR)).glob("index-*.json")
    )
    return index_files[-1] if len(index_files) > 0 else None


def check_for_reply(binary_dir: str = os.getcwd()) -> bool:
    """ """
    return get_reply_index(binary_dir) is not None


def read_reply_index(binary_dir=os.getcwd()):
    """
    Reads the reply index file
    """

    index_file = get_reply_index(binary_dir)
    with open(index_file, "r", encoding="utf-8") as f:
        index = json.load(f)

    assert index["reply"]["client-ctool"]["codemodel-v2"]["kind"] == "codemodel"

    try:
        codemodel_file = index["reply"]["client-ctool"]["codemodel-v2"]["jsonFile"]
        codemodel_path = os.path.join(binary_dir, REPLY_DIR, codemodel_file)
        load_codemodel(codemodel_path)
    except KeyError:
        pass


def load_codemodel(path):
    """
    Read in a cmake-file-api codemodel v2
    """

    data = json.load(path)

    assert data.get("kind") == "codemodel"

    # read all the target jsonFiles
    reply_dir = os.path.dirname(path)
    for config in data["configurations"]:
        for target in config["targets"]:
            load_target(os.path.join(reply_dir, target["jsonFile"]))


def load_target(path):
    """
    Read in a cmake-file-api target object
    """

    data = json.load(path)

    name = data["name"]

    dependencies = []
    try:
        # relative paths are relative to the source directory
        dependencies = list(
            set(dependencies + [source["path"] for source in data["sources"]])
        )
    except KeyError:
        pass

    try:
        # relative paths in the backtraceGraph::files list are relative to the source directory
        dependencies = list(set(dependencies + data["backtraceGraph"]["files"]))
    except KeyError:
        pass

    print(f"{name} depends on {dependencies}")
