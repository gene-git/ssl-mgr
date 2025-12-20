# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Read text file and return data & timestamps
"""
import os

from .read_write import open_file


def read_file_time(fpath: str, binary: bool = False) -> tuple[str, int, int]:
    """
    Read tlsa file and file time stamps.

    Args:
        fpath (str):
            FIle to read

        binary (bool):
            Optional - if true file is read using 'rb'
            otherwise 'r' (text). Defaults to False.

    Returns:
        tuple[data:str, atime: int, mtime: int]

        Times are in nanosecs.
        data is empty string ('') if file not found
    """
    data = ''
    nothing = ('', -1, -1)
    if not fpath:
        return nothing

    try:
        stat = os.stat(fpath)
    except OSError:
        return nothing

    mode = 'rb' if binary else 'r'
    fob = open_file(fpath, mode)
    if not fob:
        return nothing

    data = fob.read()
    fob.close()

    return (data, stat.st_atime_ns, stat.st_mtime_ns)
