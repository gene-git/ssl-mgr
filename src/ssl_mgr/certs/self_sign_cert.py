# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Crypto primative - certs
"""
# pylint: disable=too-many-locals
from datetime import datetime, timezone, timedelta

from cryptography.x509 import load_pem_x509_certificate
from cryptography import x509

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PrivateKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey

from .hash import lookup_hash
from .class_csr import SslCsr
from .save_pem import save_chain_pem, save_fullchain_pem, save_cert_pem

#------------------------------------------------
# cert signed by our own (self-signed) root cert
#------------------------------------------------
def own_sign_cert(db_dir:str, ssl_ca:'SslCA', ssl_csr:SslCsr):
    """
    Have CA make a signed cert from CSR
    """
    myname = 'own_sign_cert'
    ca_svc = ssl_ca.svc

    #
    # Get CA key
    #
    ca_privkey_pem = ssl_ca.cert.key.privkey_pem
    if not ca_privkey_pem :
        print(f'Error {myname}: Signing CA has No private key')
        return (None, None)
    ca_key = load_pem_private_key(ca_privkey_pem, password=None)

    #
    # CA Cert
    #
    ca_cert_pem = ssl_ca.cert.cert
    if not ca_cert_pem :
        print(f'Error {myname}: Signing CA has no cert')
        return (None, None)
    ca_cert = load_pem_x509_certificate(ca_cert_pem )

    #
    # Our chain is CA fullchain
    # Our full chain is cert + chain
    #
    chain_pem = ssl_ca.cert.fullchain
    if not chain_pem :
        print(f'Error {myname}: Signing CA has no fullchain')
        return (None, None)

    #
    # csr = x509.CertficateSigningRequest
    #
    csr = ssl_csr.csr
    csr_subject = csr.subject
    csr_pubkey = csr.public_key()

    #
    # Hash type
    # - for ed25519 and ed448 hash must be None
    #
    digest = ca_svc.ca.digest
    if not digest:
        digest = 'sha384'
    hash_type = lookup_hash(digest)

    if isinstance(ca_key, EllipticCurvePrivateKey):
        curve = ca_key.curve
        if curve in (Ed25519PrivateKey, Ed448PrivateKey):
            hash_type = None

    #
    # Make cert:
    #
    issuer = ca_cert.subject

    time_start =  datetime.now(timezone.utc)
    days_to_end = max(30, ca_svc.ca.sign_end_days)
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

    #cert.set_version(2)
    cert = cert_bld.sign(ca_key, hash_type)

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
        fullchain_pem  = chain_pem

    save_cert_pem(cert_pem, db_dir)
    save_chain_pem(chain_pem, db_dir)
    save_fullchain_pem(fullchain_pem, db_dir)

    return (cert_pem, chain_pem)

#------------------------------------------------
#           self signed root cert
#------------------------------------------------
def _self_signed_root_cert(ssl_cert:'SslCert', ssl_csr:SslCsr):
    """
    Self signed root cert - not signed (other than self)
    """
    logs = ssl_cert.logs
    svc = ssl_cert.svc
    privkey_pem = ssl_cert.key.privkey_pem

    #
    # private key
    #
    if not privkey_pem :
        logs('Error: Missing private key from for self signed cert')
        return None
    key = load_pem_private_key(privkey_pem, password=None)

    #
    # csr = x509.CertficateSigningRequest
    #
    csr = ssl_csr.csr
    csr_subject = csr.subject
    csr_pubkey = csr.public_key()   # should be same as key.public_key()

    #
    # Hash type
    #
    digest = svc.ca.digest
    if not digest:
        digest = 'sha384'

    hash_type = lookup_hash(digest)
    if isinstance(key, EllipticCurvePrivateKey):
        curve = key.curve
        if curve in (Ed25519PrivateKey, Ed448PrivateKey):
            hash_type = None

    #
    # Make cert:
    #
    issuer = csr_subject

    time_start =  datetime.now(timezone.utc)
    days_to_end = min(30, svc.ca.sign_end_days)
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

    cert = cert_bld.sign(key, hash_type)

    #
    # serialize to PEM
    #
    cert_pem = cert.public_bytes(encoding=serialization.Encoding.PEM)

    return cert_pem

def self_signed_root_cert(ssl_cert:'SslCert', db_dir:str, ssl_csr:SslCsr):
    """
    A root cert is not signed by another CA.
    Its just a self-signed cert.
    """
    cert_pem = _self_signed_root_cert(ssl_cert, ssl_csr)

    #
    # Save cert, chain, fullchain
    #  - chain = cert (since self signed)
    # fullchain can be cert or cert + cert
    #
    chain_pem = cert_pem
    fullchain_pem  = chain_pem

    save_cert_pem(cert_pem, db_dir)
    save_chain_pem(chain_pem, db_dir)
    save_fullchain_pem(fullchain_pem, db_dir)

    return (cert_pem, chain_pem)
