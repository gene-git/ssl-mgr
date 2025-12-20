# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
File database

top = /etc/ssl-mgr/data or /opt/Local/etc/ssl-mgr ./ when testing
group = "ca" or "example.com"
service  = ca: "ca-sub1".  client domain: "mail" "web" ...
<top_dir>
  <group>/
     <service>/
       curr -> db/<date-time>
       next -> db/<date-time>
       prev -> db/<date-time>

       db/<date-tiime1>
       db/<date-tiime2>
  work_dir = <top><group>/<service>
"""
# pylint: disable=too-many-instance-attributes,invalid-name
# pylint: disable=too-few-public-methods
import os

from utils import make_dir_path
from utils import Log


class SslDbData:
    """
    Manage ssl databases
    """
    def __init__(self, top_dir: str, grp_name: str, svc_name: str) -> None:
        self.okay: bool = True

        self.top_dir: str = top_dir
        self.group: str = grp_name
        self.service: str = svc_name

        self.work_dir: str = ''
        self.db_dir: str = ''
        self.cb_dir: str = ''

        self.link_names: tuple[str, str] = ('curr', 'next')
        self.db_names: dict[str, str] = {}

        logger = Log()
        logs = logger.logs
        if not (top_dir and grp_name):
            txt = f'top_dir ({top_dir}) group ({grp_name})'
            logs(f'SslDb requires: {txt}')
            self.okay = False
            return
        #
        # work_dir
        #
        self.work_dir = os.path.join(top_dir, 'certs', grp_name)

        if os.path.exists(self.work_dir):
            if not os.path.isdir(self.work_dir):
                logs(f'SslDb: must be a directory: {self.work_dir}')
                self.okay = False
                return
        else:
            is_okay = make_dir_path(self.work_dir)
            if not is_okay:
                self.okay = False

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None
