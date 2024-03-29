# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  File database
  <top_dir>                # top      = /etc/ssl-mgr/data or /opt/Local/etc/ssl-mgr ./ when testing
        <group>/           # group    = "ca" or "example.com"
            <service>/     # service  = ca: "ca-sub1".  client domain: "mail" "web" ...
                curr -> db/<date-time>
                next -> db/<date-time>
                prev -> db/<date-time>

                    db/<date-tiime1>
                    db/<date-tiime2>
  work_dir = <top><group>/<service>
"""
# pylint: disable=too-many-instance-attributes,invalid-name
import os
from utils import get_logger
from utils import make_dir_path
from .new_next import new_next
from .next_to_curr import next_to_curr
from .init_service import init_service

class SslDb:
    """
    Manage ssl databases
    """
    def __init__(self, top_dir: str, grp_name: str, svc_name: str) -> None:
        self.okay = True

        self.top_dir = top_dir
        self.group = grp_name
        self.service = svc_name

        self.work_dir = None
        self.db_dir = None
        self.cb_dir = None

        self.logger = get_logger()
        self.log = self.logger.log
        self.logs = self.logger.logs
        self.logsv = self.logger.logsv

        if not (top_dir and grp_name ) :        #and service):
            self.logs(f'SslDb requires: top_dir ({top_dir}) group ({grp_name})')
            self.okay = False
            return
        #
        # work_dir
        #
        self.work_dir = os.path.join(top_dir, 'certs', grp_name)

        if os.path.exists(self.work_dir):
            if not os.path.isdir(self.work_dir):
                self.logs(f'SslDb : must be a directory: {self.work_dir}')
                self.okay = False
                return
        else:
            is_okay = make_dir_path(self.work_dir)
            if not is_okay:
                self.okay = False

        #
        # svc_dir
        #
        if svc_name:
            init_service(self, svc_name, self.logs)

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None

    def get_curr_path(self):
        """ return what curr link points to """
        pcurr = None
        dcurr = self.db_names.get('curr')
        if dcurr:
            pcurr = os.path.join(self.db_dir, dcurr)
        return pcurr

    def get_next_path(self):
        """ return what curr link points to """
        pnext = None
        dnext = self.db_names.get('next')
        if dnext:
            pnext = os.path.join(self.db_dir, dnext)
        return pnext

    def get_path(self, lname):
        """ returns path to db_name for lname (curr, next) """
        if lname == 'curr':
            return self.get_curr_path()

        if lname == 'next':
            return self.get_next_path()

        return None

    def new_next(self, date_str:str=None) -> bool:
        """
         Make new db/date and set next to point to it
          - allow caller to set date_str so can use same one for application run
        """
        if not new_next(self, date_str=date_str):
            self.okay = False
        return self.okay

    def next_to_curr(self) -> bool:
        """
        Update
            curr ==> prev
            next ==> curr
            next ==> None
        """
        if not next_to_curr(self):
            self.okay = False
        return self.okay
