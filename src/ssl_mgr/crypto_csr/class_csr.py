# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certificate Tools - CSR
"""
# pylint: disable=too-many-instance-attributes,invalid-name

from ssl_mgr.db import SslDb
from ssl_mgr.config_service import ServiceConf

from .csr_build import csr_generate
from .csr_file import (read_csr, write_csr)
from .csr_data import SslCsrData


class SslCsr(SslCsrData):
    """
    Certificate Signing Request
    """
    def __init__(self,
                 db_name: str,
                 svc: ServiceConf,
                 db: SslDb,
                 is_ca: bool = False):

        super().__init__(db_name, svc, db, is_ca)

        #
        # read existing csr if available
        #
        self.read()

    def generate(self, privkey_pem: bytes) -> bool:
        """
        Make a CSR
         Input:  privkey_pem
         Output: CSR in PEM format
        """
        if not privkey_pem:
            print('Error: Generate CSR requires private key')
            self.okay = False
            return False

        (self.csr, self.csr_pem) = csr_generate(self, privkey_pem)
        if not self.csr:
            print('Failed to make CSR')
            self.okay = False
            return False
        return True

    def read(self) -> None:
        """
        read csr from file
         - ok to get nothing as may not be any CSR
        """
        (self.csr, self.csr_pem) = read_csr(self.db_dir, self.file)

    def save(self) -> bool:
        """ write csr to it's file """
        is_okay = write_csr(self.csr_pem, self.db_dir, self.file)
        if not is_okay:
            print(f'Error writing csr file to {self.db_dir}')
            self.okay = False
        return self.okay
