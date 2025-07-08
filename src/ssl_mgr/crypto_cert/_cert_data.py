# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certs, chains, clients
"""
# pylint: disable=too-many-instance-attributes, invalid-name,
# pylint: disable=too-many-arguments, too-few-public-methods
#
#

import os

from db import SslDb
from config import SslOpts
from config_service import ServiceConf
from crypto_base import (read_chain_pem, read_cert_pem, read_fullchain_pem)
from crypto_csr import SslCsr

from .class_key import SslKey


class CertData():
    """
    Cert, csr, chain, keys
     - for all key types (rsa, ec)
     NB Cert doesn't know if its curr/next (just symlinks)
        It only knows it's actual dir :
        topdir/group/service/db/date/db.db_dir/db_name
    """
    # pylint: disable=too-many-positional-arguments
    def __init__(self, db_name: str, svc: ServiceConf, db: SslDb,
                 grp_name: str, svc_name: str, opts: SslOpts):
        self.db_name: str = db_name
        self.svc: ServiceConf = svc
        self.group: str = grp_name
        self.service = svc_name
        self.db = db
        self.db_dir = os.path.join(db.db_dir, db_name)
        self.okay = True
        self.keyopts = svc.keyopts
        self.opts = opts

        #
        # All services in 'ca' group are certificate authorities
        #
        self.is_ca = False
        if grp_name and grp_name.lower() == 'ca':
            self.is_ca = True

        #
        # read existing certs, chains etc
        #  All in PEM format
        # todo: change attrib name: self.cert -> cert->cert_pem
        #
        self.cert: bytes = b''
        self.chain: bytes = b''
        self.fullchain: bytes = b''
        self.csr: SslCsr                # Data
        self.csr_pem: bytes = b''
        self.key: SslKey

        if self.db_dir:
            self.cert = read_cert_pem(self.db_dir)
            self.chain = read_chain_pem(self.db_dir)
            self.fullchain = read_fullchain_pem(self.db_dir)

        self.key = SslKey(self.db_name, self.svc, self.db)
        self.csr = SslCsr(self.db_name, self.svc,
                          self.db, is_ca=self.is_ca)

        #
        # If svc newer than cert - cert out of date
        #
        if (self.cert_ftime_nanosecs
                and svc.ftime_nanosecs < self.cert_ftime_nanosecs):
            self.cert_out_of_date = False

    def __getattr__(self, name: str):
        """ Unknown attribs return None instead of error """
        return None
