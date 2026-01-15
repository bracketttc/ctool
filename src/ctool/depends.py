"""
ctool depends command and related functions
"""

import argparse
import platform
import sys
from dataclasses import dataclass

from . import util

LINUX_RELEASE = {"rpm": ["rhel", "fedora", "centos"], "dpkg": ["debian", "ubuntu"]}


@dataclass(frozen=True)
class PackageProvider:
    """ """

    id: str


def system_default_package_manager() -> str:
    """
    Use heuristics to determine the system's package manager
    """
    release_map = {"rpm": ["rhel", "fedora", "centos"], "dpkg": ["debian", "ubuntu"]}

    if hasattr(platform, "freedesktop_os_release"):
        release = platform.freedesktop_os_release()
        for manager, ids in release_map.items():
            if release["ID"] in ids:
                return manager
            for id_like in release["ID_LIKE"].split():
                if id_like in ids:
                    return manager

    return "unknown"


def list_dependencies(manager: str) -> list[str]:
    """
    Generate a list of dependencies from CMake build system
    """

    deps: list[str] = []

    if manager == "rpm":
        for dep in deps:
            print(f"rpm -q --whatprovides '{dep}'")
    elif manager == "dpkg":
        pass

    return []


def install_dependencies(deps: list[str], manager: str, sudo: str):
    """
    Install missing dependencies
    """

    if manager == "rpm":
        pass
    elif manager == "dpkg":
        pass


def main():
    """
    entry point for ctool depends
    """

    parser = argparse.ArgumentParser("ctool depends")
    parser.add_argument(
        "--package-manager",
        action="store",
        choices=["dpkg", "rpm"],
        default=system_default_package_manager(),
        help="Tell `ctool depends` what kind of package manager to use",
        nargs=1,
    )
    subparsers = parser.add_subparsers(
        title="Subcommands",
        description="What to do with dependency information",
        dest="subcommand",
    )
    subparsers.add_parser(
        "list", help="List dependencies known to the build system [default]"
    )
    install_parser = subparsers.add_parser(
        "install", help="Install missing dependencies"
    )
    install_parser.add_argument("--sudo")
    args = parser.parse_args()

    if not args.subcommand or args.subcommand == "list":
        print("List")
    elif args.subcommand == "install":
        print("Install")

    sys.exit(0)
