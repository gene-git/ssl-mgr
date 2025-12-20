# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
  CA class
"""
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods, too-many-instance-attributes
import time

from utils import Log
from config import (SslOpts, CAInfo)
from db import SslDb
from dns_base import SslDns
from config_service import ServiceConf
from ca_sign import (CACertbot)
from crypto_cert import CASelf
from crypto_cert import CALocal
from crypto_cert import SslCert


class ServiceData():
    """
    Service Data base class for a single group-service pair.
    Group can be CA (Own or letencrypt) or Client (i.e. one domain)
    """
    def __init__(self, grp_name: str, svc_name: str,
                 opts: SslOpts, ssl_dns: SslDns | None):
        """
        grp_name := 'ca'
        """
        self.okay: bool = True
        self.grp_name: str = grp_name
        self.apex_domain: str = grp_name
        self.svc_name: str = svc_name
        self.opts: SslOpts = opts
        self.ssl_dns: SslDns | None = ssl_dns

        #
        # Service details (includes conf.d/group/service)
        #
        self.svc = ServiceConf(opts, grp_name, svc_name)
        if not self.svc.okay:
            self.okay = False
            return

        self.db = SslDb(opts.top_dir, grp_name, svc_name)

        #
        # Certificate Authority (root or signing authority)
        #
        self.ca_self: CASelf | None = None
        self.ca_local: CALocal | None = None
        self.ca_certbot: CACertbot | None = None

        if not self.ca_init():
            self.okay = False
            return

        #
        # Certs includes keys, certs, csrs and chains
        #
        self.link_names = ('curr', 'next')      # , 'prev')
        self.cert: dict[str, SslCert] = {}
        for (_lname, db_name) in self.db.db_names.items():
            if db_name:
                self.cert[db_name] = SslCert(db_name, self.svc, self.db,
                                             grp_name, svc_name, opts)

        #
        # save initial next cert time
        # Cert changed => either next-to-curr
        #              or next/cert is newer
        #
        self.now_ns = time.time_ns()
        self.curr_cert_changed = False
        self.next_cert_changed = False

    def __getattr__(self, name):
        """ Unknown attribs return None instead of error """
        return None

    def ca_init(self) -> bool:
        """
        Initialize CA.

         CA info: self or certbot (letsencrypt)
         used to sign our cert
          - only missing (None) for a root CA

         3 cases indicated by ca_name and/or ca_info.type
           - signing_ca = 'self' or empty
             this is a self signed cert (basically the root)
             Handled by: self_signed_root_cert()
             Note: 'self' is preferred, empty for backward compat'
             Not signed by any other entity

           - ca_info.type = 'self' or "local"
               Signed by a local self-signed root cert
               self is a minomer since it is signed by CA
               but the CA is a local CA
               So "local" is preferred

          - ca_info.type = 'certbot' or 'letsencrypt'
               letsencrypt using certbot
        """
        self.ca_self = None
        self.ca_local = None
        self.ca_certbot = None

        logger = Log()
        logs = logger.logs

        #
        # Which CA will sign the cert.
        # Self (or None for older configs) if self signed cert.
        #
        ca_name = self.svc.signing_ca

        ca_info = self.opts.ca_infos.get_info(ca_name)

        if not ca_name or ca_name == 'self':
            if not ca_info:
                ca_info = CAInfo()
            ca_info.ca_name = 'self'
            ca_info.ca_type = 'self'
            self.ca_self = CASelf(ca_info, self.opts)
            self.ca_self.test = self.opts.test
            self.ca_self.debug = self.opts.debug

        else:
            if not ca_info:
                logs(f'Error: unknown signing CA : {ca_name}')
                return False

            ca_info_type = ca_info.ca_type.lower()
            if ca_info_type in ('self', 'local'):
                self.ca_local = CALocal(ca_info, self.opts)
                self.ca_local.test = self.opts.test
                self.ca_local.debug = self.opts.debug

            elif ca_info_type in ('certbot', 'letsencrypt'):
                self.ca_certbot = CACertbot(ca_info, self.opts)
                self.ca_certbot.test = self.opts.test
                self.ca_certbot.dry_run = self.opts.dry_run
                self.ca_certbot.debug = self.opts.debug

            else:
                logs(f'Error: unkown ca_info type : {ca_info_type}')
                return False

        if self.opts.debug:
            self.svc.debug = self.opts.debug
        return True
