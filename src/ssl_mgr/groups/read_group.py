# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Read ny variables from conf.d/<group>/ssl-group.conf
"""
import os
from typing import (Any)

from utils import read_toml_file
from .group import SslGroup


def _dict_to_sslgroup(ssl_group: SslGroup, data: dict[str, Any]):
    """
    map dictioanry to class instance
    """
    if not data:
        return

    for (key, val) in data.items():
        setattr(ssl_group, key, val)


def read_group_conf(ssl_group: SslGroup):
    """
    Load up application config
    """
    conf_dir = ssl_group.opts.conf_dir
    grp_name = ssl_group.grp_name
    conf_file = os.path.join(conf_dir, grp_name, 'ssl-group.conf')
    conf_dict = read_toml_file(conf_file)
    _dict_to_sslgroup(ssl_group, conf_dict)
