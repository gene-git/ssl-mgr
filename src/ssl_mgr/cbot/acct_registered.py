# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Check if an LE account exists
"""
import os

from ssl_mgr.utils import dir_list


def acct_registered(cb_dir: str, staging: bool = False) -> bool:
    """
    Determine if have LE account
    (can always pass down reg info)
    cb_dir=./group/service/cb
    Check for presence of
       <cb_dir>/<domain>/accounts/acme-v02.api.letsencrypt.org/directory/???
         meta.json, private_key.json
    """
    stage = ''
    if staging:
        stage = '-staging'

    lets = f'acme{stage}-v02.api.letsencrypt.org'

    dir_1 = os.path.join(cb_dir, 'accounts', lets, 'directory')

    if not os.path.isdir(dir_1):
        return False

    #
    # get list of fingerprint dirs - account details under that
    #
    (_files, fp_dirs, _links) = dir_list(dir_1, path_type='path')
    if not fp_dirs:
        return False

    for fpd in fp_dirs:
        meta = os.path.join(fpd, 'meta.json')
        pkey = os.path.join(fpd, 'private_key.json')
        if os.path.exists(meta) and os.path.exists(pkey):
            return True
    return False
