# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Read variables from conf.d/ssl-mgr.conf
"""
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
from typing import (Any)
import os
from utils import read_toml_file

from .services_list import (is_wildcard_services, service_list_from_dir)
from ._opts_data import SslOptsData


def read_ssl_mgr_conf(opts: SslOptsData) -> dict[str, Any]:
    """
    Read up application config
     - convert dictionary provided by toml reader
       into SslOpts class instance
    """
    conf_dir = opts.conf_dir
    conf_file = os.path.join(conf_dir, 'ssl-mgr.conf')
    conf_dict = read_toml_file(conf_file)

    if not conf_dict:
        return conf_dict

    #
    # [[groups]]        # array of tables
    #   domain='..'
    #   services=[...]
    #   active=..
    #
    groups = conf_dict.get('groups')
    if not groups or not isinstance(groups, list):
        print('Error: config groups missing - must be list of tables')
        return conf_dict

    grps_svcs = {}
    for item in groups:
        domain = item.get('domain')

        services = item.get('services')
        if is_wildcard_services(services):
            services = service_list_from_dir(conf_dir, domain)

        active = item.get('active')
        if not active:
            continue

        if domain and services:
            grps_svcs[domain] = services
        else:
            txt = f'domain={domain} services={services}'
            print(f'Warning: Config has bad active item : {txt}')

    #
    # Keeping toml globals in their own section reduces chance
    # of variable being attached to a diff section if section is
    # above globals. So we always kepe globals in their own section.
    # For our code - we Map globals to top level
    #
    conf_globals = conf_dict.get('globals')

    old_renew_map: dict[str, str] = {
            'renew_expire_days': 'renew_target_90',
            'renew_expire_days_spread': 'rand_adj_90',
            }
    conf_renew_old: dict[str, float] = {}

    if conf_globals:
        for (key, value) in conf_globals.items():
            if key in old_renew_map:
                print(f'Warning: deprecated {key}. See [renew_info] in docs')
                new_key = old_renew_map[key]
                conf_renew_old[new_key] = float(value)
            else:
                conf_dict[key] = value
        del conf_dict['globals']

    #
    # Conf renew
    #
    conf_renew: dict[str, float] = {}
    info = conf_dict.get('renew_info')
    if info:
        # if missing and available in old globals use old
        conf_renew = info
        for (key, value) in conf_renew_old.items():
            if not conf_renew.get(key):
                conf_renew[key] = value
    else:
        conf_renew = conf_renew_old

    conf_dict['renew_info'] = conf_renew
    conf_dict['grps_svcs'] = grps_svcs

    return conf_dict
