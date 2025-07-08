# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
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
import os

from ._db_data import SslDbData
from .new_next import new_next
from .next_to_curr import next_to_curr
from .init_service_dirs import init_service_dirs


class SslDb(SslDbData):
    """
    Manage ssl databases
    """
    def __init__(self, top_dir: str, grp_name: str, svc_name: str):
        """
        Inherit from data base class
        """
        super().__init__(top_dir, grp_name, svc_name)

        #
        # Service info directories
        #
        if svc_name:
            init_service_dirs(self, svc_name)

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

    def new_next(self, date_str: str = '') -> bool:
        """
        Make new db/date and set next to point to it
        - allow caller to set date_str so can use
          same one for application run
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
