# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  CA class
"""
# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
import time
from utils import get_logger
from db import SslDb
from ssl_svc import SslSvc
from certs import SslCert
from certs import SslCA
from .class_state import SvcState
from .service_to_production import service_to_production
from .service_tasks import check_curr_cert_changed, check_next_cert_changed
from .service_tasks import new_key_pair, new_next, new_csr, new_cert
from .service_tasks import copy_curr_to_next, next_to_curr, renew_cert, roll_next_to_curr
from .service_tasks import svc_tlsa_generate
from .service_time import time_to_renew
from .cert_status import cert_status

class Service():
    """
    For a single group-service pair.
    Group can be CA (Own or letencrypt) or Client (i.e. one domain)
    """
    def __init__(self, grp_name:str, svc_name:str, opts:'SslOpts', ssl_dns):
        """
        grp_name := 'ca'
        """
        self.okay = True
        self.grp_name = grp_name
        self.apex_domain = grp_name
        self.svc_name = svc_name
        self.opts = opts
        self.ssl_dns = ssl_dns

        self.logger = get_logger()
        self.log = self.logger.log
        self.logs = self.logger.logs
        self.logsv = self.logger.logsv

        #
        # Service details (includes conf.d/group/service)
        #
        self.svc = SslSvc(opts, grp_name, svc_name)
        if not self.svc.okay:
            self.okay = False
            return

        self.db = SslDb(opts.top_dir, grp_name, svc_name)

        #
        # CA used to sign our cert
        #  - only missing (None) for a root CA
        #
        if self.svc.signing_ca:
            self.ca = SslCA(self.svc.signing_ca, self.opts)
            if self.opts.debug:
                self.svc.debug = self.opts.debug
            self.ca.test = self.opts.test
            self.ca.dry_run = self.opts.dry_run

        #
        # Certs includes keys, certs, csrs and chains
        #
        self.link_names = ('curr', 'next')      # , 'prev')
        self.cert = {}
        for (_lname, db_name) in self.db.db_names.items():
            if db_name:
                self.cert[db_name] = SslCert(db_name, self.svc, self.db, grp_name, svc_name, opts)

        #
        # Current state
        #
        self.state = SvcState(self)

        #
        # save initial next cert time
        # Cert changed => either next-to-curr
        #              or next/cert is newer
        #
        self.now_ns = time.time_ns()
        self.curr_cert_changed = False
        self.next_cert_changed = False
        self.curr_cert_time = self.state.curr.cert_time
        self.next_cert_time = self.state.next.cert_time

    def __getattr__(self, name):
        """ Unknown attribs return None instead of error """
        return None

    def cert_status(self):
        """ display cert status for curr/next """
        return cert_status(self)

    def check_cert_changed(self):
        """ check for changed cert """
        curr_changed = check_curr_cert_changed(self)
        next_changed = check_next_cert_changed(self)
        return (curr_changed, next_changed)

    def to_production(self, prod_svc_dir):
        """
        Copy certs/keys to production
        """
        if not service_to_production(self, prod_svc_dir):
            self.okay = False
        return self.okay

    def new_next(self):
        """
        New next dir - where all work happens
        """
        return new_next(self)

    def new_key_pair(self):
        """ display cert status for curr/next """
        return new_key_pair(self)

    def new_csr(self):
        """ display cert status for curr/next """
        return new_csr(self)

    def new_cert(self):
        """ display cert status for curr/next """
        return new_cert(self)

    def time_to_renew(self):
        """ check if cert is expiring """
        return time_to_renew(self)

    def renew_cert(self):
        """
        make new_cert only if current cert is expiring
        """
        if not renew_cert(self):
            self.okay = False
        return self.okay

    def tlsa_generate(self):
        """
        Generate DNS TLSA records for curr/next
        """
        return svc_tlsa_generate(self)

    def copy_curr_to_next(self):
        """
        Create new next and copy over
        current key and CSR - retain time stamp
        """
        if not copy_curr_to_next(self):
            self.okay = False
        return self.okay

    def roll_next_to_curr(self):
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

# -------------------------------------------------------------------------------------------------
