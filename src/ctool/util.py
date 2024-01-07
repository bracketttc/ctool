"""
ctool utility functions
"""


def remove_prefix(text, prefix):
    """
    Remove a prefix from a string (if present).

    Python 3.9 strings have `removeprefix`, but we support back to 3.6.
    """
    if text.startswith(prefix):
        return text[len(prefix) :]
    return text
