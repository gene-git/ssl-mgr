# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Generate TLSA resource record file(s)
"""
# pylint: disable=too-many-locals
import os
from utils import copy_file_atomic

def tlsa_to_production(group:'SslGroup', prod_group_dir:str):
    """
    Copy the tlsa.<apex_domain> to production apex_domain dir (aka prod_group_dir)
    """
    logsv = group.logs

    src_path = group.tlsa_path
    filename = os.path.basename(src_path)
    dst_path = os.path.join(prod_group_dir, filename)

    if group.opts.debug:
        logsv(f'  tlsa_to_production: {src_path} -> {dst_path}')
    else:
        okay = copy_file_atomic(src_path, dst_path)
        if not okay:
            return False
    return True
