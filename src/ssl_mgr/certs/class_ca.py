# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  CA class
"""
# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from db import SslDb
from utils import get_logger
from ssl_svc import SslSvc
from .class_csr import SslCsr
from .class_cert import SslCert
from .class_cainfo import CAInfo
from .sign_cert import sign_cert

class SslCA():
    """
    CA used to sign our cert. Signing CAs used by:
     - clients (domains)
       - signed by local intermediate (sub) CA
       - signed by letsencrypt
     - local sub CA itself gets signed by local root CA
    """
    def __init__(self, ca_name:str, opts:'SslOpts'):
        self.okay = True
        self.group = 'ca'
        self.service = ca_name
        self.ca = None
        self.svc = None
        self.opts = opts

        #
        # Options to pass to CA
        #
        self.test = False
        self.dry_run = False
        self.debug = False

        # get what we need to know from ca-info file
        if not ca_name :
            return

        self.logger = get_logger()
        self.log = self.logger.log
        self.logs = self.logger.logs
        self.logsv = self.logger.logsv

        #
        # info is high level description of this CA
        #  - comes from ca-info.conf
        #
        self.info = CAInfo()
        if not self.info.init_ca_name(opts.top_dir, ca_name):
            self.logs(f'Error: Unknown signing CA {ca_name}')
            self.logs(f'       Add {self.service} to conf.d/ca-info.conf')
            self.okay = False
            return

        if self.info.ca_type == 'self':
            #
            # For local CA read svc config
            #   N/A for letsencrypt
            #
            self.svc = SslSvc(opts, self.group, self.service)

            self.db = SslDb(opts.top_dir, self.group, self.service)
            db_name = self.db.db_names['curr']
            if not db_name:
                self.logs('Error: CA has no current cert/keys')
                self.okay = False
                return

            self.cert = SslCert(db_name, self.svc, self.db, self.group, self.service, opts)

    def sign_cert(self, db_dir:str, ssl_csr:SslCsr) -> (bytes, bytes):
        """
        Create signed cert from the CSR
        """
        (signed_cert, chain) = sign_cert(self, db_dir, ssl_csr)
        return (signed_cert, chain)
