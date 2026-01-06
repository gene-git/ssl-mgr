# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
  CA class
"""
# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes

from ssl_mgr.config import SslOpts
from ssl_mgr.dns_base import SslDns
from ssl_mgr.utils import Log

from .service_tasks import (check_curr_cert_changed, check_next_cert_changed)
from .service_tasks import (new_key_pair, new_next, new_csr, new_cert)
from .service_tasks import (copy_curr_to_next, next_to_curr)
from .service_tasks import (renew_cert, roll_next_to_curr)
from .service_tasks import svc_tlsa_generate

from .service_to_production import service_to_production
from .service_time import (time_to_renew, get_expiration_text)
from .cert_status import cert_status
from ._service_data import ServiceData
from .class_state import SvcState


class Service(ServiceData):
    """
    For a single group-service pair.
    Group can be CA (Own or letencrypt) or Client (i.e. one domain)
    """
    def __init__(self, grp_name: str, svc_name: str,
                 opts: SslOpts, ssl_dns: SslDns | None):
        """
        Use base class ServiceData
        """
        super().__init__(grp_name, svc_name, opts, ssl_dns)
        if not self.okay:
            return

        #
        # Current state
        #
        self.state = SvcState(self)

        #
        # save initial curr/next cert time
        # Pull it from state
        # Can we drop this now that it is in 'state'
        # NB These are file modify times.
        #
        self.curr_cert_time = self.state.curr.cert_time
        self.next_cert_time = self.state.next.cert_time

    def cert_status(self):
        """ display cert status for curr/next """
        return cert_status(self)

    def check_cert_changed(self):
        """ check for changed cert """
        curr_changed = check_curr_cert_changed(self)
        next_changed = check_next_cert_changed(self)
        return (curr_changed, next_changed)

    def to_production(self, prod_svc_dir: str) -> bool:
        """
        Copy certs/keys to production
        """
        if not service_to_production(self, prod_svc_dir):
            self.okay = False
        return self.okay

    def new_next(self) -> bool:
        """
        New next dir - where all work happens
        """
        return new_next(self)

    def new_key_pair(self) -> bool:
        """ display cert status for curr/next """
        return new_key_pair(self)

    def new_csr(self) -> bool:
        """ display cert status for curr/next """
        return new_csr(self)

    def new_cert(self) -> bool:
        """ generate a new cert for next """
        logger = Log()
        expiration_text = get_expiration_text(self, 'curr')
        if expiration_text:
            logger.logs(expiration_text, opt='mspace')

        return new_cert(self)

    def time_to_renew(self) -> tuple[bool, str]:
        """ check if cert is expiring """
        return time_to_renew(self)

    def renew_cert(self) -> bool:
        """
        make new_cert only if current cert is expiring
        """
        if not renew_cert(self):
            self.okay = False
        return self.okay

    def tlsa_generate(self) -> bool:
        """
        Generate DNS TLSA records for curr/next
        """
        return svc_tlsa_generate(self)

    def copy_curr_to_next(self) -> bool:
        """
        Create new next and copy over
        current key and CSR - retain time stamp
        """
        if not copy_curr_to_next(self):
            self.okay = False
        return self.okay

    def roll_next_to_curr(self) -> bool:
        """
        Must be done >= 2xTTL of any DNS tlsa records
         - next must exist no auto create without --force
         - check for next being cert/keys being older > min_roll_mins
           wont run without force
        """
        return roll_next_to_curr(self)

    def next_to_curr(self):
        """
        Make next the new curr
        """
        return next_to_curr(self)
