# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certificate Tools
"""
import os
from typing import (Any)

from ssl_mgr.utils import write_toml_file
from ssl_mgr.utils import Log

from .service_conf_data import ServiceConfData


def _ssl_svc_to_dict(svc: ServiceConfData) -> dict[str, str]:
    """
    Map ssl svc to dictionary to be written as toml file
    """
    dic: dict[str, Any] = {}

    logger = Log()
    logs = logger.logs

    if not svc:
        logs('Error: missing svc - cannot map input to dict')
        return dic

    for (key, val) in vars(svc).items():
        if key in ('x509', 'keyopts', 'ca'):
            dic[key] = {}
            for (skey, sval) in vars(val).items():
                dic[key][skey] = sval
        else:
            dic[key] = val
    return dic


def write_svc(svc: ServiceConfData,
              targ_dir: str,
              ) -> bool:
    """
    write svc to targ_dir/file
    - we replace svc_dir before writing
    """
    logger = Log()
    logs = logger.logs

    if not os.path.isdir(targ_dir):
        logs(f'Error:  write svc : not a directory : {targ_dir}')
        return False

    path = os.path.join(targ_dir, svc.file)
    dic = _ssl_svc_to_dict(svc)

    if not write_toml_file(dic, path):
        return False
    return True
