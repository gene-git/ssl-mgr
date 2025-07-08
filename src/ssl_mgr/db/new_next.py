# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Set up a new "next" directory and symlink
"""
# pylint: disable=invalid-name
import os

from utils import current_date_time_str
from utils import (make_dir_path, make_symlink)

from ._db_data import SslDbData


def new_next(db: SslDbData, date_str: str = '') -> bool:
    """
    Make new db/date and set next symlink to point to it
     - allow caller to set date_str so can use same one for application run
    """
    lnext = 'next'
    if not date_str:
        date_str = current_date_time_str()

    db.db_names[lnext] = date_str
    path_next = os.path.join(db.db_dir, date_str)

    is_okay = make_dir_path(path_next)
    if not is_okay:
        return False

    #
    # Set the 'next' symlink
    #
    lname_path = os.path.join(db.work_dir, lnext)
    path_rel = os.path.join('db', date_str)
    make_symlink(path_rel, lname_path)

    return True
