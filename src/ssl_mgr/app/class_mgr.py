# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  ssl-mgr application Class
   - Application works on one or more group-service pairs.
   - Doing multiples, allows a single DNS update which is more efficient.
"""
# pylint: disable=too-many-instance-attributes
import os
from groups import SslGroup, GroupChanges
from utils import current_date_time_str, get_my_hostname
from utils import init_logging, get_logger
from config import SslOpts
from config import check_options, check_options_cbot_hook, check_options_group

from .class_lock import SslLockMgr
from .tasks import execute_tasks

class SslMgr():
    """
    SSL manager class
    """
    def __init__(self):
        self.cwd = os.getcwd()
        self.now = current_date_time_str()

        self.okay = True
        self.verb = False

        (self.this_host, self.this_fqdn) = get_my_hostname()

        #
        # svc[group] = [svc1, svc2, ...]
        #
        self.groups = {}
        self.changes = GroupChanges()

        #
        # Get config and command line options
        #
        self.opts = SslOpts()

        #
        # initialize logger (needs logdir from config)
        #
        init_logging(self.opts.logdir)
        self.logger = get_logger()
        self.logger.set_verb = self.opts.verb
        self.log = self.logger.log          # logfile
        self.logs = self.logger.logs        # logfile + stdout
        self.logsv = self.logger.logsv      # logfile + stdout(if verbose)

        #
        # Get lock - wait if not available
        #
        self.lockmgr = SslLockMgr(self.opts.conf_dir)
        if not self.lockmgr.acquire():
            # Shouldn't happen - should always be able to get lock
            self.okay = False
            self.logs('Error : failed to get lock')
            return

        if not check_options(self.logs, self.opts):
            self.okay = False
            self.logs('Error: with config/options')
            return
        if not check_options_cbot_hook(self.logs, self.opts):
            self.okay = False
            self.logs('Error: with Certbot config')
            return

        #
        # Groups & Services:
        #   group : ca or apex_domain
        #
        for (grp_name, svcs) in self.opts.grps_svcs.items():
            if not check_options_group(self.logs, grp_name, svcs, self.opts):
                self.okay = False
                return

            this_group = SslGroup(grp_name, svcs, self.opts)
            if this_group.okay:
                self.groups[grp_name] = this_group
            else:
                self.logs(f'Error: {grp_name} failed to initialize')
                self.okay = False
                return

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None

    def do_tasks(self):
        """
        Run whatever been tasked to do
        """
        return execute_tasks(self)
