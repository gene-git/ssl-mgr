# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Tools
"""
from typing import Callable

import os
from utils import write_toml_file

def _ssl_svc_to_dict(svc:"SslSvc", log:Callable[[str], None]) -> dict:
    """
    Map ssl svc to dictionary to be written as toml file
    """
    if not svc:
        log('Error: missing svc - cannot map input to dict')
        return None

    dic = {}
    for (key, val) in vars(svc).items():
        #if key in ('x509', 'keyopts', 'ca', 'dns'):
        if key in ('x509', 'keyopts', 'ca'):
            dic[key] = {}
            for (skey, sval) in vars(val).items():
                dic[key][skey] = sval
        else:
            dic[key] = val
    return dic

def write_svc(svc, targ_dir:str, log:Callable[[str], None]) -> None:
    """
    write svc to targ_dir/file
    - we replace svc_dir before writing
    """
    if not os.path.isdir(targ_dir):
        log(f'Error:  write svc : not a directory : {targ_dir}')
        return False

    path = os.path.join(targ_dir, svc.file)
    dic = _ssl_svc_to_dict(svc, log)

    if not write_toml_file(dic, path):
        return False
    return True
