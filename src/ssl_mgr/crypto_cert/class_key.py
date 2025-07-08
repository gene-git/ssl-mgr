# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Crypto primative - keys
"""
# pylint: disable=invalid-name,too-many-instance-attributes

import os

from db import SslDb
from crypto_base import save_privkey_pem
from crypto_base import read_privkey_pem
from config_service import ServiceConf

from .keys import gen_key_rsa
from .keys import gen_key_ec
from .keys import priv_to_pub_key


class SslKey():
    """ Key class for either RSA and EC keys """
    def __init__(self, db_name: str, svc: ServiceConf, db: SslDb):
        self.okay: bool = True
        self.db_name: str = db_name
        self.svc: ServiceConf = svc
        self.db: SslDb = db
        self.db_dir: str = ''
        self.keyopts: ServiceConf.KeyOpts = svc.keyopts

        self.key_dir: str = ''
        self.privkey_pem: bytes = b''
        self.pubkey_pem: bytes = b''
        # self.privkey:
        # self.pubkey:

        self.db_dir = os.path.join(db.db_dir, db_name)

        # Not error for no key
        self.read_privkey()

    def __getattr__(self, name: str):
        """ non-set items simply return None so easy to check existence"""
        return None

    def refresh_paths(self) -> bool:
        """
        After any change to curr/next update to ensure
        path references up to date
        """
        db_name = self.db_name
        self.db_dir = os.path.join(self.db.db_dir, db_name)
        self.read_privkey()
        return self.okay

    def save_privkey(self) -> bool:
        """
        write priv key file
        """
        self.okay = save_privkey_pem(self.privkey_pem, self.db_dir)
        return self.okay

    def read_privkey(self) -> bool:
        """
        read priv key file
        """
        self.privkey_pem = read_privkey_pem(self.db_dir)
        if not self.privkey_pem:
            return False
        return True

    def set_key_opts(self, keyopts: ServiceConf.KeyOpts) -> bool:
        """
        save key options
        If keys exist not matching option they should be deleted.
        """
        self.keyopts = keyopts
        return self.okay

    def new_key_pair(self) -> bool:
        """
        generate key pair
        """
        match self.keyopts.ktype:
            case 'rsa':
                self.privkey_pem = gen_key_rsa(self.keyopts.rsa_bits)
            case 'ec' | _:
                self.privkey_pem = gen_key_ec(self.keyopts.ec_algo)

        if self.privkey_pem:
            self.pubkey_pem = priv_to_pub_key(self.privkey_pem)
        else:
            self.okay = False
        return self.okay
