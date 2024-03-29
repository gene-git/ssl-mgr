# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
DNS support tools
"""
# pylint: disable=duplicate-code
import os
from utils import copy_file_atomic

# python 3.12+ -> dns_dir can be path or list of paths : type[str | [str]]
def dns_zone_update(dns_path:str, dns_dir, debug:bool=False, log=print) -> bool:
    """
    Copies dns_path to one or more directories dns_dir
     - The dns_dir/dns_path(s) are then included by the dns zone file
     - Used by cbot/auth_push to push acme-challenge RR
     - Used by ssl-mgr to push updated TLSA RR
    """
    #
    # save DNS RR file
    #
    if not dns_path:
        log('Error dns_zone_update: Missing dns file to copy')
        return False

    if not dns_dir:
        log(f'Error dns_zone_update: copy {dns_path} missing destination directory/directories')
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
            log(f'debug dns_zone_update : {dns_path} -> {dst_path}')
        else:
            okay = copy_file_atomic(dns_path, dst_path)
            if not okay:
                return False
    return True
