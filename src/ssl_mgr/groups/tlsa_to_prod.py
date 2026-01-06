# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Generate TLSA resource record file(s)
"""
# pylint: disable=too-many-locals
import os

from ssl_mgr.utils import copy_file_atomic
from ssl_mgr.utils import Log

from .group_data import GroupData


def tlsa_to_production(group: GroupData, prod_group_dir: str) -> bool:
    """
    Copy the tlsa.<apex_domain> to production
    apex_domain dir (aka prod_group_dir)
    """
    logger = Log()
    log = logger.log
    logsv = logger.logs

    src_path = group.tlsa_path
    filename = os.path.basename(src_path)
    dst_path = os.path.join(prod_group_dir, filename)

    if group.opts.debug:
        logsv(f'  tlsa_to_production: {src_path} -> {dst_path}')
    else:
        okay = copy_file_atomic(src_path, dst_path, log=log)
        if not okay:
            return False
    return True
