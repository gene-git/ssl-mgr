# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
# pylint: disable=too-many-branches
"""
Check if cert is expiring
"""
import cryptography
from cryptography import x509
from cryptography.x509 import NameOID
from cryptography.x509 import Extensions
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509 import load_pem_x509_csr
from cryptography.x509 import CertificateSigningRequest
from cryptography.x509 import ObjectIdentifier
from cryptography.x509 import NameAttribute
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import ed448
# from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric import x448
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key

from .crypto_types import (KeyTypePrvOther, KeyTypePubOther)
from .crypto_types import (KeyTypePrv, KeyTypePub)

from .cert_expires import CertExpires
from .certinfo import CertInfo


def cert_time_to_expire(cert: x509.Certificate) -> tuple[str, int]:
    """
    Returns cert expiration days relative to now
     - negative means already expired
    N.B. cryptography as of version 42 not_valid_after is deprecated.
         time zone must be used. Must change to:
        - not_valid_after_utc
    Returns
        (expiry_date, days_left)
    """
    if not cert:
        return ('', -1)

    expires = cert_expires(cert)
    if expires:
        expiry_date_str = expires.expiration_date_str()
        days = int(expires.days())        # truncated
    else:
        expiry_date_str = '-'
        days = -1

    return (expiry_date_str, days)


def get_name_field(x509_name: x509.Name, name_oid: ObjectIdentifier) -> str:
    """
    extract x509.NAME field
    Args:
        x509_name (x509.Name):

        name_oid (ObjectIdentifier)
        e.g. NameOID.COMMON_NAME

    Returns:
        the string value (take from first in list as should
        only be 1 item returned for our use case)
    """
    item = ''
    items: list[NameAttribute] = []
    if x509_name:
        items = x509_name.get_attributes_for_oid(name_oid)
        if items:
            val = items[0].value
            if isinstance(val, bytes):
                item = val.decode()
            else:
                item = val
    return item


def get_sans(extensions: Extensions) -> list[str]:
    """
    extract sans
    """
    san_names: list[str] = []
    if not extensions:
        return san_names

    try:
        sans_ext = extensions.get_extension_for_class(
                x509.SubjectAlternativeName)
        if sans_ext:
            sans = sans_ext.value
            if sans:
                san_names = sans.get_values_for_type(x509.DNSName)
                ipas = sans.get_values_for_type(x509.IPAddress)
                if ipas:
                    ips = [str(ip) for ip in ipas]
                    san_names += ips
        return san_names

    except cryptography.x509.ExtensionNotFound:
        san_names = []
        return san_names


def key_info(key: KeyTypePrv | KeyTypePub | KeyTypePrvOther | KeyTypePubOther
             ) -> CertInfo:
    """
    Suports more key types than used for signing etc.
    This way it helps us identify more key types
    than used by us or cryptography module for signing
    which is also limited in key types.
    """
    info = CertInfo()

    if isinstance(key, ec.EllipticCurvePrivateKey):
        curve = key.curve.name
        info.key_algo_str = f'prvkey-{curve}'

    elif isinstance(key, ec.EllipticCurvePublicKey):
        curve = key.curve.name
        info.key_algo_str = f'pubkey-{curve}'

    elif isinstance(key, rsa.RSAPublicKey):
        key_size = key.key_size
        info.key_algo_str = f'pubkey-rsa-{key_size}'

    elif isinstance(key, rsa.RSAPrivateKey):
        key_size = key.key_size
        info.key_algo_str = f'prvkey-rsa-{key_size}'

    elif isinstance(key, dsa.DSAPublicKey):
        key_size = key.key_size
        info.key_algo_str = f'pubkey-dsa-{key_size}'

    elif isinstance(key, dsa.DSAPrivateKey):
        key_size = key.key_size
        info.key_algo_str = f'prvkey-dsa-{key_size}'

    elif isinstance(key, ed25519.Ed25519PrivateKey):
        info.key_algo_str = 'prvkey-ed25519'

    elif isinstance(key, ed25519.Ed25519PublicKey):
        info.key_algo_str = 'pubkey-ed25519'

    elif isinstance(key, ed448.Ed448PrivateKey):
        info.key_algo_str = 'prvkey-ed448'

    elif isinstance(key, ed448.Ed448PublicKey):
        info.key_algo_str = 'pubkey-ed448'

    elif isinstance(key, x448.X448PrivateKey):
        info.key_algo_str = 'prvkey-x448'

    elif isinstance(key, x448.X448PublicKey):
        info.key_algo_str = 'pubkey-x448'

    elif isinstance(key, dh.DHPrivateKey):
        key_size = key.key_size
        info.key_algo_str = f'prvkey-dh-{key_size}'

    else:
        info.key_algo_str = 'key type unknown'
    return info


def csr_info(csr: CertificateSigningRequest) -> CertInfo:
    """
    Summary fields of CSR
    """
    # pylint: disable=protected-access
    info: CertInfo = CertInfo()

    # pubkey
    pubkey = csr.public_key()
    subinfo = key_info(pubkey)  # fills key_algo_str
    info.pubkey_info = subinfo.key_algo_str

    # subject
    info.subject_rfc4514 = csr.subject.rfc4514_string()
    info.subject_CN = get_name_field(csr.subject, NameOID.COMMON_NAME)
    info.sans = get_sans(csr.extensions)

    # signature
    # algo is really same info as pubkey + hash
    # we dont have pubkey of signer only pubkey of subject
    if csr.signature_hash_algorithm:
        info.sig_hash = csr.signature_hash_algorithm.name
        info.sig_algo = csr.signature_algorithm_oid._name
    # info.sig_algo = f'{info.pubkey_info}-{info.sig_hash}'

    return info


def cert_expires(cert: x509.Certificate) -> CertExpires | None:
    '''
    Return CertExpires instance
    '''
    if not cert:
        return None

    expires = CertExpires(cert.not_valid_before_utc, cert.not_valid_after_utc)
    return expires


def cert_info(cert: x509.Certificate) -> CertInfo:
    """
    Extract useful info from cert
    """
    # pylint: disable=protected-access
    info = CertInfo()
    if not cert:
        return info

    # expiration
    expires = cert_expires(cert)
    if expires:
        info.expires = expires

        info.expiry_date_str = expires.expiration_date_str()
        info.days_left = int(expires.days())        # truncated
        info.seconds_left = expires.seconds()
        info.expiry_string = expires.expiration_string()

        info.issue_date_str = expires.issue_date_str()
        info.issue_days_ago = int(expires.issue_days())
        info.issue_seconds_ago = expires.issue_seconds()
        info.issue_string = expires.issue_string()

    # issuer
    if cert.issuer:
        info.issuer_rfc4514 = cert.issuer.rfc4514_string()
        info.issuer_CN = get_name_field(cert.issuer, NameOID.COMMON_NAME)
        info.issuer_O = get_name_field(cert.issuer, NameOID.ORGANIZATION_NAME)

    # subject
    if cert.subject:
        info.subject_rfc4514 = cert.subject.rfc4514_string()
        info.subject_CN = get_name_field(cert.subject, NameOID.COMMON_NAME)
        info.sans = get_sans(cert.extensions)

    # public key info
    subinfo = key_info(cert.public_key())
    info.pubkey_info = subinfo.key_algo_str

    # sig
    # algo is really same info as pubkey + hash
    # we dont have pubkey of signer only pubkey of subject
    if cert.signature_hash_algorithm:
        info.sig_hash = cert.signature_hash_algorithm.name
        info.sig_algo = cert.signature_algorithm_oid._name
    # info.sig_algo = f'{info.pubkey_info}-{info.sig_hash}'

    return info


def cert_pem_info(cert_pem: bytes) -> CertInfo:
    """
    Extract info from certificate pem bytes
    """
    cert = load_pem_x509_certificate(cert_pem)
    info = cert_info(cert)

    return info


def key_pem_info(key_pem: bytes) -> CertInfo:
    """
    Extract info from key pem bytes
    """
    info = CertInfo()
    try:
        key_prv = load_pem_private_key(key_pem, password=None)
        if key_prv:
            info = key_info(key_prv)

    except ValueError:
        try:
            key_pub = load_pem_public_key(key_pem)
            if key_pub:
                info = key_info(key_pub)

        except ValueError:
            pass
    return info


def csr_pem_info(csr_pem: bytes) -> CertInfo:
    """
    Extract info from CSR pem bytes
    """
    try:
        csr = load_pem_x509_csr(csr_pem)
        info = csr_info(csr)
    except ValueError:
        info = CertInfo()

    return info
