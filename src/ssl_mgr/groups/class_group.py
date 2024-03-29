# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  group (ca or apex domain) class
"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=invalid-name
import os
from ssl_dns import init_primary_dns_server
from ssl_dns import dns_file_hash
from utils import get_logger
from db import SslDb
from services import Service
from .avail_services import available_services
from .class_tasks import TaskMgr
from .group_tasks import group_to_production
from .group_tasks import execute_tasks
from .class_change import GroupChange

class SslGroup():
    """
    Group is either a 'CA' or an 'Apex Domain'
    It holds a collection of services.
     - Called from ssl_mgr
     - grp_name:svcs are from command line options and passed in here
    """
    def __init__(self, grp_name:str, svcs:[str], opts:"SslOpts"):
        self.okay = True
        self.grp_name = grp_name          # If not CA this is apex_domain name
        self.apex_domain = grp_name
        self.opts = opts
        self.ssl_dns = None
        self.svcs = svcs

        # hash lets us know if anything changed
        self.tlsa_path = None             # Final tlsa.<apex_domain> file
        self.tlsa_hash_before = None
        self.tlsa_hash_after = None
        self.tlsa_changed = False
        self.cert_changed = False
        self.curr_cert_changed = False
        self.next_cert_changed = False

        self.db = None
        top_dir = opts.top_dir

        self.logger = get_logger()
        self.log = self.logger.log
        self.logs = self.logger.logs
        self.logsv = self.logger.logsv

        self.ssl_dns = init_primary_dns_server(opts, grp_name)
        self.db = SslDb(opts.top_dir, grp_name, None)

        # check state of tlsa file
        tlsa_file = f'tlsa.{self.apex_domain}'
        self.tlsa_path = os.path.join(self.db.work_dir, tlsa_file)
        self.tlsa_hash_before = dns_file_hash(self.tlsa_path)

        #
        # Initialize each service
        #  - services are defined in conf.d/xxx
        #  - ALL means all available services
        #
        self.services = []

        if not svcs:
            return

        # If all services, then get the fill list of available svcs
        if 'ALL' in svcs:
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
        self.task_mgr = TaskMgr(self.opts, self.logs)
        self.change = GroupChange()

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None

    def do_tasks(self):
        """
        Run whatever been tasked to do
        """
        return execute_tasks(self)

    def to_production(self, prod_group_dir):
        """
        Copy certs/keys, tlsa file -> <prod_group_dir>/<service>/xxx.pem
        ssl_mgr requests this if all groups comeplete without error
            we do not do it here even if this group has no errors
        """
        return group_to_production(self, prod_group_dir)

    def cleanup(self):
        """
        Do we need to ask each service to clean itself?
        """
