## SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certs, chains, clients
"""
# pylint: disable=too-many-instance-attributes,invalid-name,too-many-arguments
#
# TODO: change names to _pem e.g. cert->x509.Certificate, cert->cert_pem
#

import os
from cryptography.x509 import load_pem_x509_certificate

from db import SslDb
from utils import get_logger

from .save_pem import read_chain_pem, read_cert_pem, read_fullchain_pem
from .save_pem import save_bundle
from .class_csr import SslCsr
from .class_key import SslKey
from .self_sign_cert import self_signed_root_cert
from .cert_hash import cert_hash
from .cert_hash import csr_hash
from .cert_hash import pubkey_hash
from .cert_info import cert_info, cert_time_to_expire

class SslCert():
    """
    Cert, csr, chain, keys
     - for all key types (rsa, ec)
     NB Cert doesn't know if its curr/next (just symlinks)
        It only knows it's actual dir :
        topdir/group/service/db/date/db.db_dir/db_name
    """
    def __init__(self, db_name:str, svc:"SslSvc", db:SslDb,
                 grp_name:str, svc_name:str, opts:"SslOpts"):
        self.db_name = db_name
        self.svc = svc
        self.group = grp_name
        self.service = svc_name
        self.db = db
        self.db_dir = os.path.join(db.db_dir, db_name)
        self.okay = True
        self.keyopts = svc.keyopts
        self.opts = opts

        self.logger = get_logger()
        self.log = self.logger.log
        self.logs = self.logger.logs
        self.logsv = self.logger.logsv

        #
        # read existing certs, chains etc
        #  All in PEM format
        #
        self.cert = None
        self.chain = None
        self.fullchain = None
        self.csr = None
        self.key = None

        if self.db_dir:
            self.cert = read_cert_pem(self.db_dir)
            self.chain = read_chain_pem(self.db_dir)
            self.fullchain = read_fullchain_pem(self.db_dir)

        self.key = SslKey(self.db_name, self.svc, self.db)
        self.csr = SslCsr(self.db_name, self.svc, self.db)

        #
        # If svc newer than cert - cert out of date
        #
        if self.cert_ftime_nanosecs and svc.ftime_nanosecs < self.cert_ftime_nanosecs:
            self.cert_out_of_date = False

    def __getattr__(self, name):
        """ Unknown attribs return None instead of error """
        return None

    def new_key_pair(self) :    #, rsa_bits: int = 4096, ec_algo: str = 'secp384r1'):
        """
        generate rsa and ec key pairs
         - new keys are always in 'next'
        """
        self.key.set_key_opts(self.svc.keyopts)
        if not self.key.new_key_pair():
            self.okay = False
        if not self.key.save_privkey():
            self.okay = False

        self.refresh_paths()
        return self.okay

    def save_privkey(self):
        """
        Write the private keys:
        """
        self.key.save_privkey()

    def get_cert_hash(self, hash_type:str='SHA256'):
        """ return hash in hex """
        return cert_hash(self.cert, hash_type)

    def get_csr_hash(self, hash_type:str='SHA256'):
        """ return hash in hex """
        return csr_hash(self.csr, hash_type)

    def get_pubkey_hash(self, hash_type:str='SHA256', serialize_fmt="DER"):
        """ return hash in hex """
        return pubkey_hash(self.cert, hash_type, serialize_fmt=serialize_fmt)

    def set_key_opts(self, keyopts:'Org.KeyOpts'):
        """
        user settable parameters for priv key
        """
        self.keyopts = keyopts
        self.key.set_key_opts(keyopts)
        return True

    def new_csr(self):
        """
        Make new csr
        """
        csr = self.csr
        if not csr.generate(self.key.privkey_pem):
            self.okay = False

        if not csr.save():
            self.okay = False
        self.refresh_paths()
        return self.okay

    def new_cert(self, signing_ca:'SslCA'):
        """
        Request siging_ca to sign our certs
         - ca should return:
           cert_pem, chain_pem
        - if not a signing ca then just create a cert
        """
        # certs/keys/chains saved in db_dir
        db_dir = self.db_dir

        csr = self.csr
        debug = False
        if self.opts and self.opts.debug:
            debug = True

        if signing_ca:
            if self.opts:
                signing_ca.test = self.opts.test
                signing_ca.dry_run = self.opts.dry_run
                signing_ca.debug = self.opts.debug
            (cert_pem, chain_pem) = signing_ca.sign_cert(db_dir, csr)
        else:
            (cert_pem, chain_pem) = self_signed_root_cert(self, db_dir, csr)

        #
        # We have cert and chain.
        # Read in fullchain and generate bundle
        # Skip if debug mode
        #
        self.cert = cert_pem
        self.chain = chain_pem
        self.fullchain = read_fullchain_pem(db_dir)

        # save bundle = key + fullchain
        if cert_pem and not debug:
            key_pem = self.key.privkey_pem
            fullchain_pem = self.fullchain
            save_bundle(key_pem, fullchain_pem, db_dir)
        self.refresh_paths()
        if not cert_pem:
            self.okay = False
        return self.okay

    def refresh_paths(self):
        """
        After any change to curr/next update to ensure path references up to date
        """
        self.db_dir = os.path.join(self.db.db_dir, self.db_name)

        self.key = SslKey(self.db_name, self.svc, self.db)
        self.csr = SslCsr(self.db_name, self.svc, self.db)

        self.cert = read_cert_pem(self.db_dir)
        self.chain = read_chain_pem(self.db_dir)
        self.fullchain = read_fullchain_pem(self.db_dir)
        return True

    def cert_expiration(self):
        """
        Returns expiration date of certificate
        """
        expiry_date_str = '-'
        days_left = -1
        if self.cert:
            cert_pem = self.cert
            cert = load_pem_x509_certificate(cert_pem)
            (expiry_date_str, days_left) = cert_time_to_expire(cert)
        return (expiry_date_str, days_left)

    def cert_info(self):
        """
        Extract useful info from cert
        """
        info = None
        if self.cert:
            cert_pem = self.cert
            cert = load_pem_x509_certificate(cert_pem)
            info = cert_info(cert)
        return info
