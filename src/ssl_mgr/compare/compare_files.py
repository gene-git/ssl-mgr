# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Compare 2 files
"""

from .hash_file_data import hash_file_data


def compare_files(fpath1: str, fpath2: str, comment_char: str = ''):
    """
    Compare 2 files.

    White space ignore and if comment_char is non empty,
    then lines starting with it are also ignored

    Args:
        fpath1 (str):
            path to first file

        fpath2 (str):
            path to seconf file

        comment_char (str):
            If non-empty, lines beginning with this are ignored.
            Default = empty string.

    Returns:
        bool:
            True if file contents are same; otherwise False
    """
    file1_hash = hash_file_data(fpath1, comment_char=comment_char)
    file2_hash = hash_file_data(fpath2, comment_char=comment_char)

    if file1_hash == file2_hash:
        return True
    return False
