# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Crypto primative - certs
"""
# pylint: disable=too-many-locals, too-many-statements
# pylint: disable=too-many-return-statements, too-many-branches
# pylint: disable=duplicate-code
from datetime import datetime, timezone, timedelta

# from cryptography.x509 import load_pem_x509_certificate
from cryptography import x509

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PrivateKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

from ssl_mgr.utils import Log
from ssl_mgr.crypto_base import valid_prvkey_type
from ssl_mgr.crypto_base import (save_chain_pem, save_fullchain_pem, save_cert_pem)
from ssl_mgr.crypto_hash import (HashAlgo, lookup_hash_algo)
from ssl_mgr.crypto_csr import SslCsrData

from ._cert_data import CertData


def _sign_cert_self(ssl_cert: CertData,
                    ssl_csr: SslCsrData
                    ) -> bytes:
    """
    Self signed root cert - not signed (other than self)
    """
    logger = Log()
    logs = logger.logs

    svc = ssl_cert.svc
    if not ssl_cert.key:
        logs('Error: Missing ssl_cert.key for self signed cert')
        return b''
    #
    # private key
    #
    privkey_pem = ssl_cert.key.privkey_pem
    if not privkey_pem:
        logs('Error: Missing private key from for self signed cert')
        return b''
    key = load_pem_private_key(privkey_pem, password=None)

    #
    # csr = x509.CertficateSigningRequest
    #
    csr = ssl_csr.csr
    if not csr:
        logs('Error: Missing CSR for self signed cert')
        return b''

    csr_subject = csr.subject
    csr_pubkey = csr.public_key()   # should be same as key.public_key()

    #
    # Hash type
    #
    if not svc.ca:
        logs('Error: Missing svc.ca which has digest for self signed cert')
        return b''

    digest = svc.ca.digest
    if not digest:
        digest = 'sha384'

    hash_algo: HashAlgo | None = lookup_hash_algo(digest)
    if isinstance(key, EllipticCurvePrivateKey):
        curve = key.curve
        if curve in (Ed25519PrivateKey, Ed448PrivateKey):
            hash_algo = None

    #
    # Make cert:
    #
    issuer = csr_subject

    time_start = datetime.now(timezone.utc)
    days_to_end = max(90, svc.ca.sign_end_days)
    time_end = time_start + timedelta(days=days_to_end)

    serial = x509.random_serial_number()

    cert_bld = x509.CertificateBuilder()
    cert_bld = cert_bld.issuer_name(issuer)
    cert_bld = cert_bld.subject_name(csr_subject)
    cert_bld = cert_bld.public_key(csr_pubkey)
    cert_bld = cert_bld.serial_number(serial)
    cert_bld = cert_bld.not_valid_before(time_start)
    cert_bld = cert_bld.not_valid_after(time_end)

    csr_extensions = csr.extensions
    for extension in csr_extensions:
        cert_bld = cert_bld.add_extension(extension.value, extension.critical)

    if not valid_prvkey_type(key):
        print('Err: private key type unsupported. Must be one of:')
        print('  Ed25519 Ed448P RSA EllipticCurve')
        return b''

    cert = cert_bld.sign(key, hash_algo)  # type: ignore[arg-type]

    #
    # serialize to PEM
    #
    cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)

    return cert_pem


def sign_cert_self(ssl_cert: CertData,
                   db_dir: str,
                   ssl_csr: SslCsrData
                   ) -> tuple[bytes, bytes]:
    """
    A root cert is not signed by another CA.
    Its just a self-signed cert.
    """
    cert_pem = _sign_cert_self(ssl_cert, ssl_csr)

    #
    # Save cert, chain, fullchain
    #  - chain = cert (since self signed)
    # fullchain can be cert or cert + cert
    #
    chain_pem = cert_pem
    fullchain_pem = chain_pem

    save_cert_pem(cert_pem, db_dir)
    save_chain_pem(chain_pem, db_dir)
    save_fullchain_pem(fullchain_pem, db_dir)

    return (cert_pem, chain_pem)
