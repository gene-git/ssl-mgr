# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
  ssl-mgr application Class
   - Application works on one or more group-service pairs.
   - Doing multiples, allows a single DNS update which is more efficient.
"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
import os

from ssl_mgr.groups import SslGroup, GroupChanges
from ssl_mgr.utils import current_date_time_str, get_my_hostname
from ssl_mgr.utils import (Log)
from ssl_mgr.config import SslOpts
from ssl_mgr.config import check_options, check_options_cbot_hook, check_options_group

from .class_lock import SslLockMgr


class SslMgrData():
    """
    SSL manager class
    """
    def __init__(self):
        self.cwd: str = os.getcwd()
        self.now: str = current_date_time_str()

        self.okay: bool = True
        self.verb: bool = False

        (self.this_host, self.this_fqdn) = get_my_hostname()

        #
        # group[group] = [svc1, svc2, ...]
        #
        self.groups: dict[str, SslGroup] = {}
        self.changes: GroupChanges = GroupChanges()

        #
        # Get config and command line options
        #
        self.opts: SslOpts = SslOpts()

        #
        # initialize logger (needs logdir from config)
        #
        # Note: log.log -> logfile
        #       log.logs ->  logfile + stdout
        #       log.logsv -> logfile + stdout(if verbose)
        #
        logger = Log()
        logger.initialize(self.opts.logdir)
        logger.set_verb(self.opts.verb)

        #
        # Get lock - wait if not available
        #
        self.lockmgr = SslLockMgr(self.opts.conf_dir)
        if not self.lockmgr.acquire():
            # Shouldn't happen - should always be able to get lock
            self.okay = False
            logger.logs('Error : failed to get lock')
            return

        if not check_options(self.opts):
            self.okay = False
            logger.logs('Error: with config/options')
            return
        if not check_options_cbot_hook(self.opts):
            self.okay = False
            logger.logs('Error: with Certbot config')
            return

        #
        # Groups & Services:
        #   group : ca or apex_domain
        #
        for (grp_name, svcs) in self.opts.grps_svcs.items():
            if not check_options_group(grp_name, svcs, self.opts):
                self.okay = False
                return

            this_group = SslGroup(grp_name, svcs, self.opts)
            if this_group.okay:
                self.groups[grp_name] = this_group
            else:
                logger.logs(f'Error: {grp_name} failed to initialize')
                self.okay = False
                return

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None
