# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Tools - CSR
"""
# pylint: disable=too-many-instance-attributes,invalid-name

import os
#import time
from db import SslDb
from ssl_svc import SslSvc
from .csr_build import csr_generate
from .csr import read_csr
from .csr import write_csr

class SslCsr():
    """
    Handle CSR
    """
    def __init__(self, db_name:str, svc:SslSvc, db:SslDb):
        self.okay = True
        self.svc = svc
        self.db = db
        self.db_name = db_name
        self.db_dir = None
        self.file = 'csr.pem'
        self.digest = 'sha384'
        self.days_end = 3650        # csr self sig valid

        self.csr = None
        self.csr_pem = None
        self.key_pkey = None

        self.db_dir = os.path.join(self.db.db_dir, db_name)

        #
        # read existing csr if available
        self.read()

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None

    def generate(self, privkey_pem):
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

    def read(self) -> None :
        """
        read csr from file
         - ok to get nothing as may not be any CSR
        """
        (self.csr, self.csr_pem) = read_csr(self.db_dir, self.file)

    def save(self):
        """ write csr to it's file """
        is_okay = write_csr(self.csr_pem, self.db_dir, self.file)
        if not is_okay:
            print(f'Error writing csr file to {self.db_dir}')
            self.okay = False
        return self.okay


#------------------------------------------------------------------------------------------
