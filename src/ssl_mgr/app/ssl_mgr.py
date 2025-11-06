# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  ssl-mgr application Class
   - Application works on one or more group-service pairs.
   - Doing multiples, allows a single DNS update which is more efficient.
"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
import os

from utils import Log
from utils import write_path_atomic
from utils import current_date_time_str

from .ssl_mgr_data import SslMgrData
from .clean import cleanup
from .certs_to_prod import certs_to_production
from .server_restarts import server_restarts
from .check_production_synced import check_production_synced


class SslMgr(SslMgrData):
    """
    SSL manager class
    """
    def do_tasks(self):
        """
        Run whatever been tasked to do
        """
        _check_production_synced(self)
        okay = _execute_tasks(self)
        return okay


def _check_production_synced(mgr: SslMgr) -> bool:
    """
    Check produciton is up to date.
    Can get our of date when there are problems
    like failing to restart server after renew
    """
    logger = Log()
    logs = logger.logs
    now = current_date_time_str()

    in_sync = check_production_synced(mgr)
    if not in_sync:
        logs(' Production resync - updating & restarting servers now')
        mgr.opts.force = True
        mgr.opts.certs_to_prod = True
        mgr.opts.force_server_restarts = True

    #
    # semaphore file so can check for latest version
    #
    semaphore_file = f'{mgr.opts.top_dir}/.flags/6_1_updated'
    semaphore_data = f'6.1 Update: production dir sync done: {now}\n'
    have_semaphore = _have_semaphore_file(semaphore_file)

    if not have_semaphore:
        if not _create_semaphore_file(semaphore_data, semaphore_file):
            logs(f'Warning: failed to create file : {semaphore_file}')
    return True


def _have_semaphore_file(file: str) -> bool:
    """
    Return true if semaphore flag exists.
    """
    return os.path.exists(file)


def _create_semaphore_file(data: str, file: str) -> bool:
    """
    Version 6.1 requires prod dir re-sync.
    Use semaphore flag to indicate if run or not.
    """
    return write_path_atomic(data, file)


def _execute_tasks(ssl_mgr: SslMgr):
    """
    execute all required tasks.

    If any errors occur along the way => exit.

    Run whatever have been tasked to do
    Group level tasks delegated down to group
    It in turn delegates service level tasks
    - Tasks: status, renew, roll
    - dev options/tasks also supported.
    """
    logger = Log()
    logs = logger.logs
    logsv = logger.logsv
    #
    # Each group executes its tasks
    #
    logs('Start group/domain tasks :', opt='ldash')
    for (grp_name, group) in ssl_mgr.groups.items():
        if not group.do_tasks():
            logs(f' Errors with {grp_name}')
            ssl_mgr.okay = False
            return False

        # keep any changes
        ssl_mgr.changes.add_group_change(grp_name, group.change)

    logs('')
    logs('Done group tasks:')
    logs('', opt='ldash')
    #
    # Tasks for app level:
    # Order is important
    #   certs changed:
    #     - copy cert/key files to production
    #       can be curr + next, or curr (can be next but need curr)
    #     - push cert/keys to all servers (web and all email servers)
    #     - if new curr (roll)
    #       - restart all email servers (internal + border)
    #         so they get the new curr keys/certs
    #   - If dns changed (tlsa records)
    #       - resign zones push to primary
    #
    # - Copy (all) certs to prod if any changed
    #   We assume nothing has messed up the unchanged ones
    # Should we change to only copy changed ones?
    #

    if not certs_to_production(ssl_mgr):
        ssl_mgr.okay = False
        return False

    if not server_restarts(ssl_mgr):
        logs('Error: server_restarts failed')
        ssl_mgr.okay = False
        return False

    #
    # Cleanup
    #
    logsv('Cleanup and release lock')
    cleanup(ssl_mgr)
    ssl_mgr.lockmgr.release()

    return ssl_mgr.okay
