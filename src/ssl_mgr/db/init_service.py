# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Initialize db for service name
"""
# pylint: disable=too-many-instance-attributes,invalid-name
import os
from utils import make_dir_path

def _get_link_targ(link:str, log) -> str:
    """
    if link exists find what it points to
    """
    if not os.path.exists(link):
        return None

    if not os.path.islink(link):
        log(f'Warning {link} not a symlink')
        return None

    link_targ = os.readlink(link)
    return link_targ

def init_service(db, svc_name:str, log=print):
    """
    Set up service dir
    """
    if not svc_name:
        return

    db.work_dir = os.path.join(db.work_dir, svc_name)

    # db holds our output
    db.db_dir = os.path.join(db.work_dir, 'db')
    if not os.path.exists(db.db_dir):
        make_dir_path(db.db_dir)

    # cb is given to certbot to do whatever it wants
    db.cb_dir = os.path.join(db.work_dir, 'cb')
    if not os.path.exists(db.cb_dir):
        make_dir_path(db.cb_dir)

    #
    # Path and real path that each symlink points to
    #  - db_names[linkname] maps linkname -> db/<date-time>
    #
    db.link_names = ('curr', 'next')
    db.db_names = {}

    for lname in db.link_names:
        lname_path = os.path.join(db.work_dir, lname)
        link_targ = _get_link_targ(lname_path, log)
        db.db_names[lname] = None

        if link_targ:
            link_targ_name = os.path.basename(link_targ)
            db.db_names[lname] = link_targ_name
