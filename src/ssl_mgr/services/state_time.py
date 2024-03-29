# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Read / Write file with 'action time' file
one action per file.
These are saved in certs/<domain>/service/state/<action>
"""
import os

def _read_state_time(fdir:str, fname:str):
    """
    Get last modified time for each "work_dir/name"
    """
    if not fdir:
        return None

    fpath = os.path.join(fdir, fname)
    try:
        stat = os.stat(fpath)
    except OSError :
        return None
    return stat.st_mtime_ns

def read_state_times(state_dir:str, fnames:[str], status:"SvcStatus"):
    """
    For each state component, check file exists and get its mtime 
    status name is filename with extension stripped off
    store result in status.
    """
    for fname in fnames:
        key_name = os.path.splitext(fname)[0]
        key_name = f'{key_name}_time'
        mtime_ns = _read_state_time(state_dir, fname)
        setattr(status, key_name, mtime_ns)
