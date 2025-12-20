# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certificate Tools - CSR
"""
# pylint: disable=too-many-locals
import ipaddress
from cryptography import x509
from cryptography.x509 import CertificateSigningRequestBuilder
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_private_key

# from cryptography.x509 import CertificateSigningRequest
# from cryptography.x509 import load_pem_x509_csr

# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives.asymmetric import ec

# from cryptography.hazmat.primitives.serialization import Encoding
# from cryptography.hazmat.primitives.serialization import NoEncryption
# from cryptography.hazmat.primitives.serialization import PrivateFormat
# from cryptography.hazmat.primitives.serialization import PublicFormat
# from cryptography.hazmat.primitives.asymmetric import ec
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives.asymmetric import dsa
# from cryptography.hazmat.primitives.asymmetric import ed25519
# from cryptography.hazmat.primitives.asymmetric import ed448
# from cryptography.hazmat.primitives.asymmetric import x25519
# from cryptography.hazmat.primitives.asymmetric import x448
# from cryptography.hazmat.primitives.asymmetric import dh

from crypto_base import valid_prvkey_type
from crypto_hash import lookup_hash_algo
from utils import (is_valid_ip4, is_valid_ip6)

from .csr_data import (SslCsrData)


def _x509_name(svc_x509) -> x509.Name:
    """
    Fill x509.Name fields from svc_x509
    """
    subject = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, svc_x509.CN),
            x509.NameAttribute(NameOID.COUNTRY_NAME, svc_x509.C),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, svc_x509.ST),
            x509.NameAttribute(NameOID.LOCALITY_NAME, svc_x509.L),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, svc_x509.O),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, svc_x509.OU),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, svc_x509.email),
            ])
    return subject


def csr_generate(ssl_csr: SslCsrData,
                 key_pem: bytes
                 ) -> tuple[x509.CertificateSigningRequest | None, bytes]:
    """
    Make a CSR
    Input:  ssl_csr, privkey
    Output: CSR
    """
    if not key_pem:
        print('Err: Generate CSR requires private key - skipped')
        return (None, b'')

    svc_x509 = ssl_csr.svc.x509
    _passphrase = None

    if not svc_x509.CN:
        print('Err: CN must be set in ServiceConf.x509.CN')
        return (None, b'')

    #
    # priv and pub keys
    # This can return more types than supported by sign()
    #
    key = load_pem_private_key(key_pem, password=None)
    pub_key = key.public_key()
    # pub_key_pem = pub_key.public_bytes(encoding=Encoding.PEM,
    #                                    format=PublicFormat.SubjectPublicKeyInfo)
    # Check the key is supported algo to sign()
    #
    if not valid_prvkey_type(key):
        print('Err: private key type unsupported. Must be one of:')
        print('  Ed25519 Ed448P RSA EllipticCurve')
        return (None, b'')

    # checkers dont understand the valid key filer
    ssl_csr.key_pkey = key      # type: ignore[assignment]

    #
    # SANS: Subject Alternative Names
    #
    sans = svc_x509.sans
    if svc_x509.CN not in svc_x509.sans:
        sans = [svc_x509.CN] + svc_x509.sans

    # alt_names = [x509.DNSName(host) for host in sans]
    # handle domain names and ipv4/ipv6 addresses
    alt_names: list[x509.GeneralName] = []
    for name in sans:
        if is_valid_ip4(name):
            ipv4 = ipaddress.IPv4Address(name)
            x509_ip = x509.IPAddress(ipv4)
            alt_names.append(x509_ip)
        elif is_valid_ip6(name):
            ipv6 = ipaddress.IPv6Address(name)
            x509_ip = x509.IPAddress(ipv6)
            alt_names.append(x509_ip)
        else:
            x509_dns_name = x509.DNSName(name)
            alt_names.append(x509_dns_name)

    #
    # Extensions
    #
    if ssl_csr.is_ca:
        basic_constraints = x509.BasicConstraints(ca=True, path_length=None)
    else:
        basic_constraints = x509.BasicConstraints(ca=False, path_length=None)

    x509_sans = x509.SubjectAlternativeName(alt_names)

    kw_key_usage = {'digital_signature': True,
                    'key_encipherment': True,
                    'key_cert_sign': ssl_csr.is_ca,
                    'key_agreement': True,
                    'content_commitment': False,
                    'data_encipherment': False,
                    'crl_sign': ssl_csr.is_ca,
                    'encipher_only': False,
                    'decipher_only': False,
                    }
    key_usage = x509.KeyUsage(**kw_key_usage)

    extended_key_usage = x509.ExtendedKeyUsage(
            [x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
             x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
             x509.oid.ExtendedKeyUsageOID.EMAIL_PROTECTION,
             x509.oid.ExtendedKeyUsageOID.CODE_SIGNING,
             x509.oid.ExtendedKeyUsageOID.TIME_STAMPING,
             ])

    #
    # key.public_key() returns type including DH types which are not valid
    # when calling for key_id as below 2 lines
    #
    subject_key_id = x509.SubjectKeyIdentifier.from_public_key(
            pub_key)  # type: ignore[arg-type]

    authority_key_id = x509.AuthorityKeyIdentifier.from_issuer_public_key(
            pub_key)  # type: ignore[arg-type]

    #
    # Set x509 Name info
    #
    subject = _x509_name(svc_x509)

    #
    # Build the CSR
    #
    csr_bld = CertificateSigningRequestBuilder(subject)

    csr_bld = csr_bld.add_extension(basic_constraints, critical=True)
    csr_bld = csr_bld.add_extension(key_usage, critical=False)
    csr_bld = csr_bld.add_extension(extended_key_usage, critical=False)
    csr_bld = csr_bld.add_extension(subject_key_id, critical=False)
    csr_bld = csr_bld.add_extension(authority_key_id, critical=False)
    csr_bld = csr_bld.add_extension(x509_sans, critical=False)

    # lookup hash type (from hashes module) from name string
    hash_algo = lookup_hash_algo(ssl_csr.digest)

    # generate the csr
    # we check for supported key types so mute mypy
    csr = csr_bld.sign(key, hash_algo)   # type: ignore[arg-type]

    # serialize to PEM
    csr_pem = csr.public_bytes(encoding=serialization.Encoding.PEM)

    return (csr, csr_pem)
