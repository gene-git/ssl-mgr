# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Convert data dictionary to class instance
"""
# pylint: disable=too-many-instance-attributes
from typing import (Any)

from ._opts_data import (SslOptsData)


def dict_to_opts(opts: SslOptsData, data_dict: dict[str, Any]):
    """
    Map config data dictionary to SslOpts class instance data
    """
    if not data_dict:
        return

    for (key, val) in data_dict.items():
        if isinstance(val, dict):
            if key in ('smtp', 'imap', 'web', 'other'):
                serv = getattr(opts, key)
                serv.from_dict(val)
                continue

            if key in ('dns'):
                dns = getattr(opts, key)
                dns.from_dict(val)
                continue

            if key in ('group', 'grps_svcs'):
                setattr(opts, key, val)
                continue

            print(f'Config parser : uknown {key} {val}')
            # unknown ignore
            continue
        setattr(opts, key, val)
