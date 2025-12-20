# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certificate Tools
"""
import os
from typing import (Any)

from utils import Log
from utils import read_toml_file
from utils import get_file_time_ns

from .dane_tls import DaneTls
from .service_conf_data import (ServiceConfData)


type SvcSubClass = (ServiceConfData.X509 | ServiceConfData.KeyOpts
                    | ServiceConfData.CA
                    )


def _do_subclass(svc: ServiceConfData,
                 key: str, val: dict[str, Any]
                 ) -> bool:
    """
    Handle subclasses:
     X609, KeyOPts and CA,

    Returns True if sub class updated else False.

    Note: sub_svc is svc.<key_lower>
          So updating sub_svc updates svc itsef.
    """
    sub_svc_updated: bool = False

    sub_svc: SvcSubClass | None
    key_low = key.lower()

    if key in ('X509', 'KeyOpts'):
        sub_svc = getattr(svc, key_low)

    elif key == 'CA':
        svc.ca = svc.CA()
        sub_svc = svc.ca

    if sub_svc:
        #
        # Fill sub class from sub dictionary
        #
        sub_svc_updated = True
        for (subkey, subval) in val.items():
            if subkey == 'rsa_bits' and isinstance(subval, str):
                subval = int(subval)
            setattr(sub_svc, subkey, subval)
    return sub_svc_updated


def _dict_to_ssl_svc(svc: ServiceConfData, dic: dict[str, Any]) -> bool:
    """
    dic is read in from toml input file and mapped
    into instance of ServiceConf.
    keys 'Org', 'Ca' and 'Dane' are mapped to corresponding class
    """
    logger = Log()
    logs = logger.logs

    if not dic or not isinstance(dic, dict):
        logs('Error - missing dict - cannot map input to class')
        return False

    for (key, val) in dic.items():
        #
        # sub classes X509, KeyOpts, CA
        #
        # key_low = key.lower()
        if isinstance(val, dict):
            sub_svc_updated = _do_subclass(svc, key, val)
            if sub_svc_updated:
                # install it (already installed)
                # setattr(svc, key_low, sub_svc)
                continue

        #
        # dane_tls: map list[list] to list[DaneTls]
        #
        if key == 'dane_tls' and isinstance(val, list):
            dane_tls: list[DaneTls] = []
            for item in val:
                one = DaneTls()
                okay = one.from_list(item)
                if not okay:
                    logs('Error parsing Dane TLS item')
                    return False
                dane_tls.append(one)
            setattr(svc, key, dane_tls)
            continue

        #
        # all other variables
        #
        setattr(svc, key, val)
    return True


def _check_svc(svc: ServiceConfData, svc_dict: dict[str, Any]) -> bool:
    """
    group is directory name and field in file
    service is filename and field in file.
    Check they are consistent
    We want them in both places to minimized human error from copy/edit.
    """
    group_file = svc_dict.get('group')
    svc_file = svc_dict.get('service')

    logger = Log()
    logs = logger.logs

    if not group_file:
        logs('  svc file missing "group"')
        return False

    if not svc_file:
        logs('  svc file missing "service"')
        return False

    if group_file != svc.group:
        logs(f'  svc group {group_file} expecting {svc.group}')
        return False

    if svc_file != svc.service:
        logs(f'  svc service {svc_file} expecting {svc.service}')
        return False

    return True


def read_svc(svc: ServiceConfData,
             top_dir: str,
             grp_name: str,
             svc_name: str,
             ) -> bool:
    """
    read svc from file
     - toml format
    """
    svc.group = grp_name
    svc.service = svc_name
    svc.file = svc_name

    logger = Log()
    logs = logger.logs

    path = os.path.join(top_dir, 'conf.d', grp_name, svc.file)
    svc_dict = read_toml_file(path)
    if not svc_dict:
        logs(f'Error: Failed to read svc file : {path}')
        return False

    # before mapping svc dict into instance variables - check ok
    if not _check_svc(svc, svc_dict):
        return False

    if not _dict_to_ssl_svc(svc, svc_dict):
        logs(f'Error: Failed to parse svc file : {path}')
        return False
    svc.ftime_ns = get_file_time_ns(path)
    return True
