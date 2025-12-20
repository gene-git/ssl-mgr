# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
DNS support tools
"""
# pylint: disable=duplicate-code
import os

from utils import (Log)
from utils import copy_file_atomic


def dns_zone_update(dns_path: str,
                    dns_dir: str | list[str],
                    debug: bool = False
                    ) -> bool:
    """
    Copies dns_path to one or more directories dns_dir
     - The dns_dir/dns_path(s) are then included by the dns zone file
     - Used by cbot/auth_push to push acme-challenge RR
     - Used by ssl-mgr to push updated TLSA RR
    """
    #
    # Logzone should be set for process
    #
    logger = Log()
    log = logger.log
    logsv = logger.logsv
    #
    # save DNS RR file
    #
    if not dns_path:
        logsv('Error dns_zone_update: Missing dns file to copy')
        return False

    if not dns_dir:
        txt = f'copy {dns_path} missing destination directory/directories'
        logsv(f'Error dns_zone_update: {txt}')
        return False

    #
    # Target is one or more directories
    #
    dns_dirs = dns_dir
    if isinstance(dns_dir, str):
        dns_dirs = [dns_dir]

    filename = os.path.basename(dns_path)
    for dest_dir in dns_dirs:
        dst_path = os.path.join(dest_dir, filename)
        if debug:
            logsv(f'debug dns_zone_update : {dns_path} -> {dst_path}')
        else:
            okay = copy_file_atomic(dns_path, dst_path, log=log)
            if not okay:
                return False
    return True
