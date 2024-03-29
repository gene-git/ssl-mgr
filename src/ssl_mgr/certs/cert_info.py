# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Check if cert is expiring
"""
from dataclasses import dataclass,field
from datetime import datetime
from dateutil import tz
import cryptography
from cryptography import x509
#from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509 import NameOID
from cryptography.x509 import Extensions
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509 import load_pem_x509_csr
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key

def _v42_plus():
    """ check if using cryptography v42 or later """
    vers = cryptography.__version__
    major = vers.split('.', maxsplit=1)[0]
    major = int(major)
    if major > 41:
        return True
    return False

def cert_time_to_expire(cert:x509.Certificate) -> (str, int):
    """
    Returns cert expiration days relative to now
     - negative means already expired
    N.B. cryptography as of version 42 not_valid_after is deprecated.
         time zone must be used. Must change to:
        - not_valid_after_utc
    Returns (days_remaining)
    """
    if not cert:
        return (-1, -1)

    if _v42_plus():
        expiry = cert.not_valid_after_utc
    else:
        expiry = cert.not_valid_after
        expiry = expiry.replace(tzinfo=tz.UTC)

    today = datetime.now(tz.UTC)

    expiry_date_str = str(expiry)

    time_to_expire = expiry - today
    days_left = time_to_expire.days
    #hours_left = int(time_to_expire.seconds/3600)

    return (expiry_date_str, days_left)


@dataclass
class CertInfo:
    """
    Useful cert info
    """
    # pylint: disable=invalid-name,too-many-instance-attributes
    expiry_date_str: str = None
    days_left :int = -1
    issuer_rfc4514: str = None
    issuer_CN: str = None
    issuer_O: str = None
    subject_rfc4514: str = None
    subject_CN: str = None
    sans: list[str] = field(default_factory=list)
    pubkey_info:str = None
    sig_algo: str = None
    sig_hash: str = None

def get_name_field(x509_name:x509.Name, name_oid:NameOID):
    """ extract x509.NAME field """
    item = None
    if x509_name:
        item = x509_name.get_attributes_for_oid(name_oid)
        if item:
            item = item[0].value
    return item

def get_sans(extensions:Extensions):
    """
    extract sans
    """
    if not extensions:
        return []
    try:
        sans = extensions.get_extension_for_class(x509.SubjectAlternativeName)
        if sans:
            sans = sans.value
            if sans:
                sans = sans.get_values_for_type(x509.DNSName)
        return sans

    except cryptography.x509.ExtensionNotFound :
        return []

def key_info(key):
    """
    ec or rsa
    """
    if isinstance(key, ec.EllipticCurvePrivateKey):
        curve = key.curve.name
        info = f'prvkey-{curve}'

    elif isinstance(key, ec.EllipticCurvePublicKey):
        curve = key.curve.name
        info = f'pubkey-{curve}'

    elif isinstance(key, rsa.RSAPublicKey):
        key_size = key.key_size
        info = f'pubkey-rsa-{key_size}'

    elif isinstance(key, rsa.RSAPrivateKey):
        key_size = key.key_size
        info = f'prvkey-rsa-{key_size}'

    else:
        info = 'key type unknown'
    return info

def csr_info(csr):
    """
    Summary fields of CSR
    """
    info = CertInfo()

    # pubkey
    pubkey = csr.public_key()
    info.pubkey_info = key_info(pubkey)

    # subject
    info.subject_rfc4514 = csr.subject.rfc4514_string()
    info.subject_CN = get_name_field(csr.subject, NameOID.COMMON_NAME)
    info.sans = get_sans(csr.extensions)

    # signature
    # algo is really same info as pubkey + hash
    # we dont have pubkey of signer only pubkey of subject
    info.sig_hash = csr.signature_hash_algorithm.name
    info.sig_algo = csr.signature_algorithm_oid._name
    #info.sig_algo = f'{info.pubkey_info}-{info.sig_hash}'

    return info

def cert_info(cert:x509.Certificate):
    """
    Extract useful info from cert
    """
    info = CertInfo()
    if not cert:
        return info

    # expiration
    (expiry_date_str, days_left) = cert_time_to_expire(cert)

    info.expiry_date_str = expiry_date_str
    info.days_left = days_left

    # issuer
    info.issuer_rfc4514 = cert.issuer.rfc4514_string()
    info.issuer_CN = get_name_field(cert.issuer, NameOID.COMMON_NAME)
    info.issuer_O = get_name_field(cert.issuer, NameOID.ORGANIZATION_NAME)

    # subject
    info.subject_rfc4514 = cert.subject.rfc4514_string()
    info.subject_CN = get_name_field(cert.subject, NameOID.COMMON_NAME)
    info.sans = get_sans(cert.extensions)

    # public key info
    info.pubkey_info = key_info(cert.public_key())

    # sig
    # algo is really same info as pubkey + hash
    # we dont have pubkey of signer only pubkey of subject
    info.sig_hash = cert.signature_hash_algorithm.name
    info.sig_algo = cert.signature_algorithm_oid._name
    #info.sig_algo = f'{info.pubkey_info}-{info.sig_hash}'

    return info

def cert_pem_info(cert_pem:bytes) -> CertInfo:
    """
    Extract info from certificate pem bytes
    """
    cert = load_pem_x509_certificate(cert_pem)
    info = cert_info(cert)

    return info

def key_pem_info(key_pem:bytes) -> str:
    """
    Extract info from key pem bytes
    """
    info = None
    try:
        key = load_pem_private_key(key_pem, password=None)
    except ValueError:
        try:
            key = load_pem_public_key(key_pem)
        except ValueError:
            pass
    if key:
        info = key_info(key)
    return info

def csr_pem_info(csr_pem:bytes) -> CertInfo:
    """
    Extract info from CSR pem bytes
    """
    info = None
    try:
        csr = load_pem_x509_csr(csr_pem)
        info = csr_info(csr)
    except ValueError:
        pass
    return info
