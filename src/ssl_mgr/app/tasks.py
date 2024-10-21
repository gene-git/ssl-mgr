# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  execute all required tasks.
  If any errors occur along the way => exit.
"""
from .clean import cleanup
from .certs_to_prod import certs_to_production
from .server_restarts import server_restarts

def execute_tasks(ssl_mgr):
    """
    Run whatever have been tasked to do
    Group level tasks delegated down to group
    It in turn delegates service level tasks
    - Tasks: status, renew, roll
    - dev options/tasks also supported.
    """
    logs = ssl_mgr.logs
    logsv = ssl_mgr.logs
    #
    # Each group executes its tasks
    #
    logs('Start group tasks :', opt='ldash')
    for (grp_name, group) in ssl_mgr.groups.items():
        if not group.do_tasks():
            logs(f' Errors with {grp_name}')
            ssl_mgr.okay = False
            return False

        # keep any changes
        ssl_mgr.changes.add_group_change(grp_name, group.change)

        #if group.tlsa_changed :
        #    tlsa_changed = True
        #    tlsa_changed_domains.append(grp_name)

        #if group.cert_changed:
        #    certs_changed = True

        #if group.curr_cert_changed:
        #    curr_certs_changed = True

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
