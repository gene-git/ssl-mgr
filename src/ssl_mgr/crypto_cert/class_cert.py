# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certs, chains, clients
"""
# pylint: disable=too-many-instance-attributes,invalid-name,too-many-arguments

import os
from cryptography.x509 import load_pem_x509_certificate

from crypto_base import (read_chain_pem, read_cert_pem, read_fullchain_pem)
from crypto_base import save_bundle
from crypto_base import CertInfo
from crypto_base import (cert_info, cert_expires, cert_time_to_expire)
from crypto_base import CertExpires

from crypto_hash import (cert_hash, csr_hash, pubkey_hash)
from crypto_csr import SslCsr
from ca_sign import (CACertbot)
from cbot import sign_cert_wrap
from utils import Log

from .class_key import SslKey
from .ca_self import CASelf
from .ca_local import CALocal

from ._cert_data import CertData
from .sign_cert_self import sign_cert_self
from .sign_cert_local import sign_cert_local


class SslCert(CertData):
    """
    Cert, csr, chain, keys
     - for all key types (rsa, ec)
     NB Cert doesn't know if its curr/next (just symlinks)
        It only knows it's actual dir :
        topdir/group/service/db/date/db.db_dir/db_name
    """
    def new_key_pair(self) -> bool:
        """
        generate rsa and ec key pairs
         - new keys are always in 'next'
        """
        logger = Log()
        logs = logger.logs

        if not self.svc or not self.key:
            logs('Error SslCert missing key/svc')
            self.okay = False
            return False

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
        if self.key:
            return self.key.save_privkey()
        return False

    def get_cert_hash(self, hash_type: str = 'SHA256') -> str:
        """
        return hash in hex
        """
        if self.cert:
            return cert_hash(self.cert, hash_type)
        return ''

    def get_csr_hash(self, hash_type: str = 'SHA256') -> str:
        """
        return hash in hex
        """
        if self.csr_pem:
            return csr_hash(self.csr_pem, hash_type)
        return ''

    def get_pubkey_hash(self, hash_type: str = 'SHA256',
                        serialize_fmt: str = "DER") -> str:
        """
        return hash in hex
        """
        if self.cert:
            return pubkey_hash(self.cert, hash_type,
                               serialize_fmt=serialize_fmt)
        return ''

    # def set_key_opts(self, keyopts: ServiceConf.KeyOpts) -> bool:
    #     """
    #     user settable parameters for priv key
    #     """
    #     self.keyopts = keyopts
    #     self.key.set_key_opts(keyopts)
    #     return True

    def new_csr(self) -> bool:
        """
        Make new csr
        """
        csr = self.csr
        if not csr or not self.key:
            print('Error new_csr: needs CSR and key')
            self.okay = False
            return False

        if not csr.generate(self.key.privkey_pem):
            self.okay = False
            return False

        if not csr.save():
            self.okay = False
        self.refresh_paths()
        return self.okay

    def new_cert_self(self, ca_self: CASelf) -> bool:
        """
        Self signed cert
         - ca should return:
           cert_pem, chain_pem
        - if not a signing ca then just create a cert
        """
        # certs/keys/chains saved in db_dir
        logger = Log()
        logs = logger.logs

        if self.opts.verb:
            ca_name = ca_self.ca_info.ca_name
            logs(f'new_cert_self: ca = {ca_name}')

        db_dir = self.db_dir

        csr = self.csr

        (cert_pem, chain_pem) = sign_cert_self(self, db_dir, csr)

        self.new_cert_finalize(db_dir, cert_pem, chain_pem)

        if not cert_pem:
            self.okay = False
        return self.okay

    def new_cert_local(self, ca_local: CALocal) -> bool:
        """
        Self signed cert
         - ca should return:
           cert_pem, chain_pem
        - if not a signing ca then just create a cert
        """
        # certs/keys/chains saved in db_dir
        db_dir = self.db_dir

        csr = self.csr

        (cert_pem, chain_pem) = sign_cert_local(db_dir, ca_local, csr)

        self.new_cert_finalize(db_dir, cert_pem, chain_pem)

        if not cert_pem:
            self.okay = False
        return self.okay

    def new_cert_certbot(self, ca_certbot: CACertbot) -> bool:
        """
        Self signed cert
         - ca should return:
           cert_pem, chain_pem
        - if not a signing ca then just create a cert
        """
        # certs/keys/chains saved in db_dir
        db_dir = self.db_dir

        csr = self.csr  # SslCsr
        # apex_domain = csr.svc.group
        # service = csr.svc.service

        if self.opts:
            ca_certbot.test = self.opts.test
            ca_certbot.dry_run = self.opts.dry_run
            ca_certbot.debug = self.opts.debug

        (cert_pem, chain_pem) = sign_cert_wrap(ca_certbot, db_dir, csr)

        self.new_cert_finalize(db_dir, cert_pem, chain_pem)

        if not cert_pem:
            self.okay = False
        return self.okay

    def new_cert_finalize(self, db_dir: str,
                          cert_pem: bytes, chain_pem: bytes):
        """
        Called after new_cert_xxx()
        We have cert and chain.
        Read in fullchain and generate bundle
        Skip if debug mode
        """
        self.cert = cert_pem
        self.chain = chain_pem
        self.fullchain = read_fullchain_pem(db_dir)

        #
        # save bundle = key + fullchain
        #
        debug = bool(self.opts and self.opts.debug)

        if cert_pem and not debug:
            key_pem = self.key.privkey_pem
            fullchain_pem = self.fullchain
            save_bundle(key_pem, fullchain_pem, db_dir)
        self.refresh_paths()

    def refresh_paths(self):
        """
        After any change to curr/next then we
        update to ensure path references up to date
        """
        self.db_dir = os.path.join(self.db.db_dir, self.db_name)

        self.key = SslKey(self.db_name, self.svc, self.db)
        self.csr = SslCsr(self.db_name, self.svc, self.db, is_ca=self.is_ca)

        self.cert = read_cert_pem(self.db_dir)
        self.chain = read_chain_pem(self.db_dir)
        self.fullchain = read_fullchain_pem(self.db_dir)
        return True

    def cert_expires(self) -> CertExpires | None:
        '''
        Returns this cert expiration as CertExpires
        '''
        if not self.cert:
            return None

        cert_pem = self.cert
        cert = load_pem_x509_certificate(cert_pem)
        expires = cert_expires(cert)
        return expires

    def cert_expiration(self) -> tuple[str, int]:
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

    def cert_info(self) -> CertInfo:
        """
        Extract useful info from cert
        """
        info = CertInfo()
        if self.cert:
            cert_pem = self.cert
            cert = load_pem_x509_certificate(cert_pem)
            info = cert_info(cert)
        return info
