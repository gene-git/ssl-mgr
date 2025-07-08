# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Crypto primative - certs
"""
# pylint: disable=too-many-locals, too-many-statements
# pylint: disable=too-many-return-statements, too-many-branches
# pylint: disable=duplicate-code
from datetime import datetime, timezone, timedelta

from cryptography.x509 import load_pem_x509_certificate
from cryptography import x509

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PrivateKey
from cryptography.hazmat.primitives.asymmetric.ec import (
        EllipticCurvePrivateKey
        )

from crypto_base import valid_prvkey_type
from crypto_base import (save_chain_pem, save_fullchain_pem, save_cert_pem)
from crypto_hash import (HashAlgo, lookup_hash_algo)
from crypto_csr import SslCsrData

from .ca_local import CALocal


def sign_cert_local(db_dir: str,
                    ca_local: CALocal,
                    ssl_csr: SslCsrData
                    ) -> tuple[bytes, bytes]:
    """
    cert signed by our own (self-signed) root cert.

    Have CA make a signed cert from CSR
    """
    myname = 'local_sign_cert'
    ca_svc = ca_local.svc

    #
    # Get CA key
    #
    if not ca_local.cert:
        print(f'Error {myname}: CA has no certificate')
        return (b'', b'')

    if not ca_local.cert.key:
        print(f'Error {myname}: CA missing key')
        return (b'', b'')

    ca_privkey_pem = ca_local.cert.key.privkey_pem
    if not ca_privkey_pem:
        print(f'Error {myname}: Signing CA has No private key')
        return (b'', b'')

    ca_key = load_pem_private_key(ca_privkey_pem, password=None)

    #
    # CA Cert
    #
    ca_cert_pem = ca_local.cert.cert
    if not ca_cert_pem:
        print(f'Error {myname}: Signing CA has no cert')
        return (b'', b'')
    ca_cert = load_pem_x509_certificate(ca_cert_pem)

    #
    # Our chain is CA fullchain
    # Our full chain is cert + chain
    #
    chain_pem = ca_local.cert.fullchain
    if not chain_pem:
        print(f'Error {myname}: Signing CA has no fullchain')
        return (b'', b'')

    #
    # csr = x509.CertficateSigningRequest
    #
    csr = ssl_csr.csr
    if not csr:
        print(f'Error {myname}: Missing CSR cannot proceed')
        return (b'', b'')

    csr_subject = csr.subject
    csr_pubkey = csr.public_key()

    #
    # Hash type
    # - for ed25519 and ed448 hash must be None
    #
    if not ca_svc.ca:
        print(f'Error {myname}: svc is missing CA piece with digest type')
        return (b'', b'')

    digest = ca_svc.ca.digest
    if not digest:
        digest = 'sha384'

    hash_algo: HashAlgo | None = lookup_hash_algo(digest)
    if isinstance(ca_key, EllipticCurvePrivateKey):
        curve = ca_key.curve
        if curve in (Ed25519PrivateKey, Ed448PrivateKey):
            # curve check needed or None for all EC curves?
            hash_algo = None

    #
    # Make cert:
    #
    issuer = ca_cert.subject

    time_start = datetime.now(timezone.utc)
    days_to_end = max(90, ca_svc.ca.sign_end_days)
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

    if not valid_prvkey_type(ca_key):
        print('Err: private key type unsupported. Must be one of:')
        print('  Ed25519 Ed448P RSA EllipticCurve')
        return (b'', b'')

    cert = cert_bld.sign(ca_key, hash_algo)  # type: ignore[arg-type]

    #
    # serialize to PEM
    #
    cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)

    #
    # Save cert, chain, fullchain
    #  - our chain = ca.fullchain
    #  - our fullchain = cert + chain
    #
    fullchain_pem = b''
    if cert_pem:
        fullchain_pem = cert_pem + chain_pem

    save_cert_pem(cert_pem, db_dir)
    save_chain_pem(chain_pem, db_dir)
    save_fullchain_pem(fullchain_pem, db_dir)

    return (cert_pem, chain_pem)
