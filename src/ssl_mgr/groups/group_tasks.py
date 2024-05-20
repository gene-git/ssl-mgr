# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  group tasks
"""
import os
from ssl_dns import dns_file_hash
from tlsa import tlsa_update_domain
from tlsa import tlsa_to_production
from tlsa import tlsa_copy_to_dns_serv

def check_tlsa_changed(group):
    """
    get hash of current tlsa file
    """
    group.tlsa_hash_after = dns_file_hash(group.tlsa_path)
    if group.tlsa_hash_after != group.tlsa_hash_before:
        return True
    return False

def group_to_production(group, prod_group_dir):
    """
    Copy all certs/keys -> production area:
        <prod_group_dir>/<service>/xxx.pem
    """
    group.logs(f'Group : {group.grp_name} to production')
    for svc in group.services:
        svc_name = svc.svc_name
        svc_dir = os.path.join(prod_group_dir, svc_name)
        svc.to_production(svc_dir)
        if not svc.okay:
            group.okay = False

    if not tlsa_update_domain(group):
        group.okay = False
        return False

    if not tlsa_to_production(group, prod_group_dir):
        group.okay = False
    return group.okay

def cleanup(_group):
    """
    ask each service to clean itself
    """

def execute_tasks_one_svc(group, svc):
    """
    Do the requested tasks
    """
    # pylint: disable=too-many-return-statements,too-many-branches
    if not group.okay:
        return False
    #
    # Order tasks: key, csr, cert then next-to-curr
    #
    logsv = group.logsv
    tasks = group.task_mgr.tasks

    if tasks.status:
        logsv('    cert status')
        if not svc.cert_status():
            return False

    if tasks.new_next:
        logsv('    new next')
        if not svc.new_next():
            return False

    if tasks.new_keys:
        logsv('    new key pair')
        if not svc.new_key_pair():
            return False

    if tasks.copy_curr_to_next:
        logsv('    curr to next')
        if not svc.copy_curr_to_next():
            return False

    if tasks.new_csr:
        logsv('    new CSR')
        if not svc.new_csr():
            return False

    if tasks.new_cert:
        logsv('    new cert')
        if not svc.new_cert():
            return False

    if tasks.renew_cert:
        logsv('    renew cert')
        if not svc.renew_cert():
            return False

    if tasks.next_to_curr:
        logsv('    next to curr')
        if not svc.next_to_curr():
            return False

    if tasks.roll_next_to_curr:
        logsv('    roll next to curr')
        if not svc.roll_next_to_curr():
            return False

    return True

def execute_tasks(group):
    """
    Do the requested tasks
    """
    # pylint: disable=too-many-return-statements,too-many-branches
    if not group.okay:
        return False

    logs = group.logs
    logsv = group.logsv
    logs(f'{group.grp_name}', opt='ldash')

    #
    # Order tasks: key, csr, cert then next-to-curr
    # Do all tasks for 1 service
    #
    tasks = group.task_mgr.tasks

    # track if any certs changed
    change = group.change
    #group.cert_changed = False
    for svc in group.services:
        logs(f'\n  {svc.svc_name}')
        #
        # check for renew_cert
        #
        if tasks.renew_cert and not svc.time_to_renew():
            continue

        if not execute_tasks_one_svc(group, svc):
            group.okay = False
            return False

        # check if one or both of curr/next cert changed
        (curr_changed, next_changed) = svc.check_cert_changed()
        change.curr_cert_changed = curr_changed
        change.next_cert_changed = next_changed
        change.cert_changed = curr_changed or next_changed
        if change.cert_changed:
            change.add_svc_name(svc.svc_name)
            logsv(f'  cert changed: {svc.svc_name} (curr, next) = ({curr_changed}, {next_changed})')

    #
    # update domain level tlsa  file
    #
    if not tlsa_update_domain(group):
        group.okay = False
        return False
    #
    # track whether:
    #   - any cert changed in group.cert_changed
    #   - tlsa changed in group.tlsa_changed
    #
    if check_tlsa_changed(group):
        change.set_tlsa_changed()

    if change.tlsa_changed:
        logsv('  TLSA changed - updating server dns zone file')
        if not tlsa_copy_to_dns_serv(group):
            group.okay = False
            return False

    # group.cleanup()

    return group.okay
