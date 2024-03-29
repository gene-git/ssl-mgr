# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Task manager
"""
# pylint: disable=too-many-instance-attributes
from dataclasses import dataclass

@dataclass
class TaskList:
    """
    Helper for what tasks need to be done
    """
    # High level tasks
    status: bool = False
    renew: bool = False
    roll: bool = False

    # low level tasks
    new_keys: bool = False
    new_csr: bool = False
    new_cert: bool = False
    renew_cert: bool = False
    push_dns: bool = False
    certs_to_prod: bool = False

    # derived tasks
    new_next: bool = False
    reuse: bool = False
    copy_curr_to_next: bool = False
    tlsa_update: bool = False
    next_to_curr: bool = False
    roll_next_to_curr: bool = False

    # options
    force: bool = False

    # check if request for new cert
    cert_change_requested: bool = False


def _is_cert_change_requested(tasks:TaskList):
    """
    Check chert change is requested or status only.
    On occasion certs in 'next' may be newer
    especially after keyboard interrupt or some problem.
    In this event, doing only --status should not push those
    'newer' files to production.
    This helps deal with that.
    """

    # high level commands
    cert_change = False
    cert_change |= tasks.renew
    cert_change |= tasks.roll

    # low level tasks
    cert_change |= tasks.new_cert
    cert_change |= tasks.renew_cert
    cert_change |= tasks.copy_curr_to_next
    cert_change |= tasks.next_to_curr
    cert_change |= tasks.roll_next_to_curr

    tasks.cert_change_requested = cert_change

class TaskMgr:
    """
    Service task support
    """
    def __init__(self, opts, logs):

        self.tasks= TaskList()
        self.logs = logs
        self.opts = opts

        self.update_tasks()
        self.check_tasks()

    def update_tasks(self):
        """
        Make the todo list
        """
        # pylint: disable=too-many-branches
        tasks = self.tasks
        opts = self.opts

        #
        # high level commands / options
        #
        tasks.status = opts.status
        tasks.renew = opts.renew
        tasks.roll = opts.roll

        tasks.reuse = opts.reuse
        tasks.force = opts.force

        #
        # low level dev commands
        #
        if opts.new_keys:
            tasks.new_keys = True

        if opts.new_csr:
            tasks.new_csr = True

        if opts.copy_csr:
            tasks.reuse = True

        if opts.new_cert:
            tasks.new_cert = True

        if opts.next_to_curr:
            tasks.next_to_curr = True

        if opts.push_dns:
            tasks.push_dns = True

        if opts.certs_to_prod:
            tasks.certs_to_prod = True

        if tasks.renew:
            if tasks.force:
                tasks.new_cert = True
            else:
                tasks.renew_cert = True

            tasks.new_csr = True
            if tasks.reuse:
                tasks.copy_curr_to_next = True
            else:
                tasks.new_keys = True
        #
        # Derived tasks
        #
        if tasks.renew or tasks.new_keys or tasks.new_csr or tasks.new_cert or tasks.reuse :
            tasks.new_next = True
            tasks.tlsa_update = True

        if tasks.roll:
            if tasks.force:
                tasks.next_to_curr = True
            else:
                tasks.roll_next_to_curr = True

            tasks.tlsa_update = True
            tasks.certs_to_prod = True

        # check if any request should lead to cert change
        _is_cert_change_requested(tasks)

    def check_tasks(self):
        """
        Checker
        """
        tasks = self.tasks
        if tasks.renew and tasks.roll:
            self.logs('Warning - renew and roll both set?')

        if tasks.renew and tasks.next_to_curr:
            self.logs('Warning - renew and next_to_curr both set?')

        if tasks.reuse and tasks.new_keys:
            self.logs('Warning - Reuse keys/certs and new keys both set?')

        if tasks.new_cert and tasks.renew_cert:
            self.logs('Warning - new cert and renew cert both set?')
