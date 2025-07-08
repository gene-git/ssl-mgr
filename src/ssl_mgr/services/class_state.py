# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  State tracker
"""
# pylint: disable=too-few-public-methods
# pylint: disable=invalid-name
import os

# from services import Service
from ._service_data import ServiceData

from .state_time import read_state_time


def _check_ready_done(predicates: list[tuple[bool, int]],
                      my_time: int
                      ) -> tuple[bool, bool]:
    """
    check if my is ready or done
    predicates = [(pred1_done, pred1_time), ...]
    preficates must be at least empty list
     - ready => all predicates are done
     - done means am ready and my_time is newer than all predicate times
    """
    my_ready = False
    my_done = False

    predicates_done = True
    for (pred_done, pred_time) in predicates:
        if not pred_done:
            predicates_done = False
            break

    if predicates_done:
        my_ready = True

    if my_time:
        predicates_older = True
        for (pred_done, pred_time) in predicates:
            if pred_time and pred_time > my_time:
                predicates_older = False

        if predicates_older:
            my_done = True
    else:
        my_done = False

    if not my_ready:
        my_done = False

    return (my_ready, my_done)


class SvcStatus:
    """
    status of each component.
     - time is file time in nanosecs
     - ready - precursor is done, item not up to date and ready to be udpated
     - done - means already up to date
    """
    # pylint: disable=too-many-instance-attributes,too-few-public-methods
    def __init__(self):
        self.svc_time: int = -1
        self.svc_ready: bool = True
        self.svc_done: bool = True

        self.privkey_time: int = -1
        self.privkey_ready: bool = False
        self.privkey_done: bool = False

        self.csr_time: int = -1
        self.csr_ready: bool = False
        self.csr_done: bool = False

        self.cert_time: int = -1
        self.cert_ready: bool = False
        self.cert_done: bool = False

        self.tlsa_time: int = -1
        self.tlsa_ready: bool = False
        self.tlsa_done: bool = False

    def update_ready_done(self):
        """
        Check predicates ready
        """
        self.privkey_ready = False
        self.privkey_done = False
        self.csr_ready = False
        self.csr_done = False
        self.cert_ready = False
        self.cert_done = False
        self.tlsa_ready = False
        self.tlsa_done = False

        #
        # privkey <= svc
        # While tecnically correct for key to depend on svc file, doing so
        # makes it impossible to reuse key and add a subdomain.
        # So we don't refresh the key (danger being change of
        # key type is not picked up).
        # If key type is changed - user must either force new
        # key or not use 'reuse key'
        # We do allow CSR to depend on svc change
        #
        predicates: list[tuple[bool, int]] = []
        (self.privkey_ready, self.privkey_done) = (
                _check_ready_done(predicates, self.privkey_time)
                )

        #
        # csr <= privkey
        #
        predicates = [(self.privkey_done, self.privkey_time),
                      (self.svc_done, self.svc_time)
                      ]
        (self.csr_ready, self.csr_done) = (
                _check_ready_done(predicates, self.csr_time)
                )

        #
        # cert <= csr
        #
        predicates = [(self.csr_done, self.csr_time)]
        (self.cert_ready, self.cert_done) = (
                _check_ready_done(predicates, self.cert_time)
                )

        #
        # tlsa <= cert
        #
        predicates = [(self.cert_done, self.cert_time)]
        (self.tlsa_ready, self.tlsa_done) = (
                _check_ready_done(predicates, self.tlsa_time)
                )


class SvcState:
    """
    Status of curr and next
    """
    def __init__(self, service: ServiceData):
        self.service = service

        self.curr = SvcStatus()
        self.next = SvcStatus()

        # NB status key is filename with extension removed
        self.fnames = ['privkey.pem', 'csr.pem', 'cert.pem', 'tlsa.rr']

        self.update()

    def update(self):
        """
        Update times and ready/done
        """
        self.update_times()
        self.update_ready_done()

    def update_times(self):
        """
        Get updated times of each key file
        """
        #
        # these symlinks can change so always retrieve
        #
        db = self.service.db
        pcurr = db.get_curr_path()
        pnext = db.get_next_path()

        # get latest file times
        read_state_times(pcurr, self.fnames, self.curr)
        read_state_times(pnext, self.fnames, self.next)

        #
        # Get svc file file at program start - program doesn't change it
        # Cant get this far without svc - so its always ready/done
        # If Org changed we are all out of date.
        #
        svc_ftime_ns = self.service.svc.ftime_ns
        self.curr.svc_done = True
        self.curr.svc_ready = True
        self.curr.svc_time = svc_ftime_ns

        self.next.svc_done = True
        self.next.svc_ready = True
        self.next.svc_time = svc_ftime_ns

    def update_ready_done(self):
        """
        Check predicates ready
        """
        self.curr.update_ready_done()
        self.next.update_ready_done()


def read_state_times(state_dir: str, fnames: list[str], status: SvcStatus):
    """
    For each state component, check file exists and get its mtime
    status name is filename with extension stripped off
    store result in status.
    """
    for fname in fnames:
        key_name = os.path.splitext(fname)[0]
        key_name = f'{key_name}_time'
        mtime_ns = read_state_time(state_dir, fname)
        setattr(status, key_name, mtime_ns)
