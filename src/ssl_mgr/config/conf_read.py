# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Read variables from conf.d/ssl-mgr.conf
"""
import os
from utils import read_toml_file
from .services_list import (is_wildcard_services, service_list_from_dir)

def read_ssl_mgr_conf(opts:"SslOpts"):
    """
    Read up application config
     - convert dictionary provided by toml reader
       into SslOpts class instance
    """
    conf_dir = opts.conf_dir
    conf_file = os.path.join(conf_dir, 'ssl-mgr.conf')
    conf_dict = read_toml_file(conf_file)

    if not conf_dict:
        return None

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
            print(f'Warning: Config has bad active item : domain={domain} services={services}')

    #
    # Keeping toml gloabls in their own section reduces chance of variable being attached
    # to a diff section if section is above globals. So we always kepe globals in
    # their own section.
    # For our code - we Map globals to top level
    #
    conf_globals = conf_dict.get('globals')
    if conf_globals:
        for (key, value) in conf_globals.items():
            conf_dict[key] = value
        del conf_dict['globals']

    conf_dict['grps_svcs'] = grps_svcs

    return conf_dict
