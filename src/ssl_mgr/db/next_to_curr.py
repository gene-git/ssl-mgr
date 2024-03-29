# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
 Make 'next' the new 'curr'
"""
# pylint: disable=invalid-name
import os
from utils import current_date_time_str
from utils import dir_list
from utils import write_path_atomic

def _has_all_needed_files(path_real:str, logs):
    """
    Check that this path holds iall the requierdd files:
     - privkey. cert, chain, fullchain, csr and bundle
    """
    all_ok = True
    required = ('privkey', 'cert', 'csr', 'chain', 'fullchain', 'bundle')

    [files_found, _dirs, _lnks] = dir_list(path_real)

    for item in required:
        file = f'{item}.pem'
        if file not in files_found:
            logs(f'Error next_to_curr: {file} missing from {path_real}')
            all_ok = False
    return all_ok


def _add_info_file(svc_name:str, fpath:str, log):
    """
    Add file to fpath with current date time
    """
    info_path = os.path.join(fpath, 'info')
    data = f'# {svc_name} rolled to curr : '
    data += current_date_time_str() + '\n'
    okay = write_path_atomic(data, info_path, log=log)
    return okay

def next_to_curr(db) -> None:
    """
    Update
        curr ==> prev
        next ==> curr
        next ==> None
    """
    lcurr = 'curr'
    lprev = 'prev'
    lnext = 'next'
    logs = db.logs

    lnext_path = os.path.join(db.work_dir, lnext)
    if not lnext_path:
        logs('Error next_to_curr: no "next" link to make "curr"')
        return False
    #
    # Before making next the new curr, ensure it has needed files
    #
    if not _has_all_needed_files(lnext_path, logs):
        return False

    curr_b4 = db.db_names[lcurr]
    next_b4 = db.db_names[lnext]

    lcurr_path = os.path.join(db.work_dir, lcurr)
    lprev_path = os.path.join(db.work_dir, lprev)
    if os.path.exists(lcurr_path) :
        if os.path.exists(lprev_path):
            os.unlink(lprev_path)
        os.rename(lcurr_path, lprev_path)
        db.db_names[lprev] = curr_b4

    os.rename(lnext_path, lcurr_path)
    db.db_names[lcurr] = next_b4
    db.db_names[lnext] = None

    #
    # Add info file in the new 'curr'
    # Ignore any write prob
    #
    _add_info_file(db.service, lcurr_path, logs)
    return True
