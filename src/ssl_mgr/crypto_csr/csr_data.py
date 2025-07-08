# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Tools - CSR
"""
# pylint: disable=too-many-instance-attributes,invalid-name
# pylint: disable=too-few-public-methods

import os
from cryptography.x509 import CertificateSigningRequest

from crypto_base import KeyTypePrv
from db import SslDb
from config_service import ServiceConf


class SslCsrData():
    """
    Data Base class for SslCst
    """
    def __init__(self,
                 db_name: str,
                 svc: ServiceConf,
                 db: SslDb,
                 is_ca: bool = False):
        """
        Base class has only the data
        """
        self.okay: bool = True
        self.svc: ServiceConf = svc
        self.db: SslDb = db
        self.db_name: str = db_name
        self.db_dir: str = ''
        self.file: str = 'csr.pem'
        self.digest: str = 'sha384'
        self.days_end: int = 3650        # csr self sig valid
        self.is_ca: bool = is_ca

        self.csr: CertificateSigningRequest | None = None
        self.csr_pem: bytes = b''
        self.key_pkey: KeyTypePrv | None = None

        self.db_dir = os.path.join(self.db.db_dir, db_name)

        #
        # Ensure is_ca is up to date
        #
        self.is_ca = is_ca

    def __getattr__(self, name: str):
        """ non-set items simply return None so easy to check existence"""
        return None
