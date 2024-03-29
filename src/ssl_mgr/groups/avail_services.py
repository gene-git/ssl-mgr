# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Misc utils
"""
import os
from utils import dir_list

def available_services(top_dir:str, grp_name:str) -> [str]:
    """
    Find all "svc" files in the config dir:
        top_dir/conf.d/service/
    to make a list of available services
    TODO: lets use active config services instead
    """
    conf_path = os.path.join(top_dir, 'conf.d', grp_name)
    [flist, _dlist, _llist] = dir_list(conf_path)

    #
    # All services are files named xxx
    #
    files = []
    if flist:
        files += flist

    services = []
    for file in files:
        services.append(file)

    return services
