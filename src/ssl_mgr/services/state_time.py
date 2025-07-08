# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Read / Write file with 'action time' file
one action per file.
These are saved in certs/<domain>/service/state/<action>
"""
import os


def read_state_time(fdir: str, fname: str) -> int:
    """
    Get last modified time for each "work_dir/name"
    """
    if not fdir:
        return 0

    fpath = os.path.join(fdir, fname)
    try:
        stat = os.stat(fpath)
    except OSError:
        return 0
    return stat.st_mtime_ns
