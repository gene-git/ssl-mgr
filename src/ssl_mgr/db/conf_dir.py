# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Config directory
"""
import os


def get_conf_dir() -> str:
    """
    Returns the current config dir
        Locate conf.d in first of (./, /etc/ssl-mgr, '/opt/Local/etc/ssl-mgr')
    """
    conf_dir = ''
    dirs = ('./', '/etc/ssl-mgr/', '/opt/Local/etc/ssl-mgr')
    conf_name = 'conf.d'
    for this_dir in dirs:
        conf_dir = os.path.join(this_dir, conf_name)
        if os.path.isdir(conf_dir):
            break
    if not conf_dir:
        print('Error: Failed to find conf.d dir')
    return conf_dir
