"""
ctool settings
"""

import configparser
import os

CONFIG_FILE = ".ctoolrc"


def configuration(source_dir=None):
    """
    Returns a configparser.ConfigParser for ctool commands
    """
    config = configparser.ConfigParser(defaults={}, inline_comment_prefixes=("#", ";"))
    userrc = os.path.join(os.path.expanduser("~"), CONFIG_FILE)
    projectrc = (
        os.path.join(source_dir, CONFIG_FILE) if source_dir is not None else CONFIG_FILE
    )
    config.read([userrc, projectrc])
    return config
