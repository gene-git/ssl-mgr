# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Misc utils
"""
import os

from ssl_mgr.config import service_list_from_dir


def available_services(top_dir: str, grp_name: str) -> list[str]:
    """
    Find all "svc" files in the config dir:
        top_dir/conf.d/service/
    to make a list of available services
    TODO: lets use active config services instead
    """
    conf_dir = os.path.join(top_dir, 'conf.d')
    service_names = service_list_from_dir(conf_dir, grp_name)

    return service_names
