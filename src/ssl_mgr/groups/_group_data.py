# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  group (ca or apex domain) class
"""
# pylint: disable=too-many-instance-attributes,m too-few-public-methods
import os

from config import (SslOpts, is_wildcard_services)
from dns_base import (SslDns, init_primary_dns_server, dns_file_hash)
from db import SslDb
from services import Service

from .avail_services import available_services
from .class_tasks import TaskMgr
from .class_change import GroupChange


class GroupData():
    """
    Group is either a 'CA' or an 'Apex Domain'
    It holds a collection of services.
     - Called from ssl_mgr
     - grp_name:svcs are from command line options and passed in here
    """
    def __init__(self, grp_name: str, svcs: list[str], opts: SslOpts):
        self.okay: bool = True
        self.grp_name: str = grp_name   # If not CA this is apex_domain name
        self.apex_domain: str = grp_name
        self.opts: SslOpts = opts
        self.ssl_dns: SslDns | None = None
        self.svcs: list[str] = svcs

        # hash lets us know if anything changed
        self.tlsa_path: str = ''             # Final tlsa.<apex_domain> file
        self.tlsa_hash_before: str = ''
        self.tlsa_hash_after: str = ''
        self.tlsa_changed: bool = False
        self.cert_changed: bool = False
        self.curr_cert_changed: bool = False
        self.next_cert_changed: bool = False

        self.db: SslDb
        top_dir: str = opts.top_dir

        self.ssl_dns = init_primary_dns_server(opts, grp_name)
        self.db = SslDb(opts.top_dir, grp_name, '')

        # check state of tlsa file
        tlsa_file = f'tlsa.{self.apex_domain}'
        self.tlsa_path = os.path.join(self.db.work_dir, tlsa_file)
        self.tlsa_hash_before = dns_file_hash(self.tlsa_path)

        #
        # Initialize each service
        #  - services are defined in conf.d/xxx
        #  - ALL means all available services
        #
        self.services: list[Service] = []

        if not svcs:
            return

        # If all services, then get the fill list of available svcs
        if is_wildcard_services(svcs):
            svcs = available_services(top_dir, grp_name)
            self.svcs = svcs

        #
        # initialize each service
        #
        for svc_name in svcs:
            this_service = Service(grp_name, svc_name, self.opts, self.ssl_dns)
            if this_service.okay:
                self.services.append(this_service)
            else:
                self.okay = False

        #
        # initialize task list
        #
        self.task_mgr = TaskMgr(self.opts)
        self.change = GroupChange()

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None
