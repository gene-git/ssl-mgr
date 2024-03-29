# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Tools
"""
from typing import Callable

import os
from utils import read_toml_file
from utils import get_file_time_ns

def _dict_to_ssl_svc(svc:"SslSvc", dic: dict, log:Callable[[str], None]) -> bool:
    """
    dic is read in from toml input file and mapped
    into instance of SslSvc.
    keys 'Org', 'Ca' and 'Dane' are mapped to corresponding class
    """
    if not dic or not isinstance(dic, dict):
        log('Error - missing dict - cannot map input to class')
        return False

    for (key, val) in dic.items():
        #
        # sections
        #
        s_svc = None
        key_low = key.lower()
        if key_low in ('x509', 'keyopts'):
            s_svc = getattr(svc, key_low)

        elif key_low == 'ca':
            svc.ca = svc.CA()
            s_svc = svc.ca

        if s_svc:
            #
            # sub dictionary
            #
            for (skey, sval) in val.items():
                if skey == 'rsa_bits' and isinstance(sval, str):
                    sval = int(sval)
                setattr(s_svc, skey, sval)
        else:
            #
            # variables
            #
            setattr(svc, key, val)
    return True

def _check_svc(svc, svc_dict, log):
    """
    group is directory name and field in file
    service is filename and field in file.
    Check they are consistent 
    We want them in both places to minimized human error from copy/edit.
    """
    group_file =  svc_dict.get('group')
    svc_file = svc_dict.get('service')

    if not group_file:
        log('  svc file missing "group"')
        return False

    if not svc_file:
        log('  svc file missing "service"')
        return False

    if group_file != svc.group:
        log(f'  svc group {group_file} expecting {svc.group}')
        return False

    if svc_file != svc.service:
        log(f'  svc service {svc_file} expecting {svc.service}')
        return False

    return True

def read_svc(svc, top_dir:str, grp_name:str, svc_name:str, log:Callable[[str], None]) -> None:
    """
    read svc from file
     - toml format
    """
    svc.group = grp_name
    svc.service = svc_name
    svc.file = svc_name

    path = os.path.join(top_dir, 'conf.d', grp_name, svc.file)
    svc_dict = read_toml_file(path)
    if not svc_dict:
        log(f'Error: Failed to read svc file : {path}')
        return False

    # before mapping svc dict into instance variables - check ok
    if not _check_svc(svc, svc_dict, log):
        return False

    if not _dict_to_ssl_svc(svc, svc_dict, log):
        log(f'Error: Failed to parse svc file : {path}')
        return False
    svc.ftime_ns = get_file_time_ns(path)
    return True
