# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Crypto primative - keys
"""
# pylint: disable=invalid-name,too-many-instance-attributes

import os
from db import SslDb
from ssl_svc import SslSvc
from .keys import gen_key_rsa
from .keys import gen_key_ec
from .keys import priv_to_pub_key
from .save_pem import save_privkey_pem
from .save_pem import read_privkey_pem

#------------------------------------------------------------------------------------------
class SslKey():
    """ Key class for either RSA and EC keys """
    def __init__(self, db_name:str, svc:SslSvc, db:SslDb):
        self.okay = True
        self.db_name = db_name
        self.svc = svc
        self.db = db
        self.db_dir = None
        self.keyopts = svc.keyopts

        self.key_dir = None
        self.privkey_pem = None
        self.pubkey_pem = None

        self.db_dir = os.path.join(db.db_dir, db_name)

        # Not error for no key
        self.read_privkey()

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None

    def refresh_paths(self):
        """
        After any change to curr/next update to ensure path references up to date
        """
        db_name = self.db_name
        self.db_dir = os.path.join(self.db.db_dir, db_name)
        self.read_privkey()
        return self.okay

    def save_privkey(self):
        """ write priv key file """
        #self.db_dir = os.path.join(self.db.db_dir, self.db_name)
        self.okay = save_privkey_pem(self.privkey_pem, self.db_dir)
        return self.okay

    def read_privkey(self):
        """ read priv key file """
        self.privkey_pem = read_privkey_pem(self.db_dir)
        if not self.privkey_pem:
            return False
        return True

    def set_key_opts(self, keyopts:'Org.KeyOpts'):
        """
        save key options
        If keys exist not matching option they should be deleted.
        """
        self.keyopts = keyopts
        return self.okay

    def new_key_pair(self):
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

#------------------------------------------------------------------------------------------
