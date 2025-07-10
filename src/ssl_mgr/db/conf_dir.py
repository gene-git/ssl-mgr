# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Config directory
"""
import os


def get_conf_dir() -> str:
    """
    Returns the current config dir
        Locate conf.d in first of (./, /etc/ssl-mgr)
    """
    # env variable takes precedence
    topdir_env: str = os.getenv('SSL_MGR_TOPDIR', '')

    top_dirs: tuple[str, str] | tuple[str, str, str]
    top_dirs = ('./', '/etc/ssl-mgr/')
    if topdir_env:
        top_dirs = (topdir_env,) + top_dirs

    conf_dir = ''
    conf_name = 'conf.d'
    for this_dir in top_dirs:
        conf_dir = os.path.join(this_dir, conf_name)
        if os.path.isdir(conf_dir):
            break
    if not conf_dir:
        print('Error: Failed to find conf.d dir')
    return conf_dir
