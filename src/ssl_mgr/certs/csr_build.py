# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Tools - CSR
"""
# pylint: disable=too-many-locals
import ipaddress
from cryptography import x509
#from cryptography.x509 import CertificateSigningRequest
from cryptography.x509 import CertificateSigningRequestBuilder
#from cryptography.x509 import load_pem_x509_csr

from cryptography.x509.oid import NameOID

#from cryptography.hazmat.primitives import hashes
#from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
#from cryptography.hazmat.primitives.asymmetric import ec

#from cryptography.hazmat.primitives.serialization import Encoding
#from cryptography.hazmat.primitives.serialization import NoEncryption
#from cryptography.hazmat.primitives.serialization import PrivateFormat
#from cryptography.hazmat.primitives.serialization import PublicFormat

from cryptography.hazmat.primitives.serialization import load_pem_private_key
from utils import (is_valid_ip4, is_valid_ip6)
from .hash import lookup_hash

def _x509_name(svc_x509) -> x509.Name :
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

def csr_generate(ssl_csr, key_pem) -> (x509.CertificateSigningRequest, bytes):
    """
    Make a CSR
    Input:  ssl_csr, privkey
    Output: CSR
    """
    if not key_pem:
        print('Err: Generate CSR requires private key - skipped')
        return None

    svc_x509 = ssl_csr.svc.x509
    _passphrase = None

    if not svc_x509.CN:
        print('Err: CN must be set in SslSvc.x509.CN')
        return None

    #
    # priv and pub keys
    #
    key = load_pem_private_key(key_pem, password=None)
    pub_key = key.public_key()
    #pub_key_pem = pub_key.public_bytes(encoding=Encoding.PEM,
    #                                   format=PublicFormat.SubjectPublicKeyInfo)

    ssl_csr.key_pkey = key

    #
    # SANS: Subject Alternative Names
    #
    sans = svc_x509.sans
    if svc_x509.CN not in svc_x509.sans:
        sans = [svc_x509.CN] + svc_x509.sans

    #alt_names = [x509.DNSName(host) for host in sans]
    # handle domain names and ipv4/ipv6 addresses
    alt_names = []
    for name in sans:
        if is_valid_ip4(name) :
            ipv4 = ipaddress.IPv4Address(name)
            x509_name = x509.IPAddress(ipv4)
        elif is_valid_ip6(name):
            ipv6 = ipaddress.IPv6Address(ipv6)
            x509_name = x509.IPAddress(ipv6)
        else:
            x509_name = x509.DNSName(name)
        alt_names.append(x509_name)

    #
    # Extensions
    #
    if ssl_csr.is_ca:
        basic_constraints = x509.BasicConstraints(ca=True, path_length=None)
    else:
        basic_constraints = x509.BasicConstraints(ca=False, path_length=None)
    sans = x509.SubjectAlternativeName(alt_names)

    kw_key_usage = {'digital_signature' : True,
                    'key_encipherment' : True,
                    'key_cert_sign' : ssl_csr.is_ca,
                    'key_agreement' : True,
                    'content_commitment' : False,
                    'data_encipherment' : False,
                    'crl_sign' : ssl_csr.is_ca,
                    'encipher_only' : False,
                    'decipher_only' : False,
                   }
    key_usage = x509.KeyUsage(**kw_key_usage)

    extended_key_usage = x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                                                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                                                x509.oid.ExtendedKeyUsageOID.EMAIL_PROTECTION,
                                                x509.oid.ExtendedKeyUsageOID.CODE_SIGNING,
                                                x509.oid.ExtendedKeyUsageOID.TIME_STAMPING,
                                               ])
    subject_key = x509.SubjectKeyIdentifier.from_public_key(pub_key)
    authority_key = x509.AuthorityKeyIdentifier.from_issuer_public_key(pub_key)

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
    csr_bld = csr_bld.add_extension(subject_key, critical=False)
    csr_bld = csr_bld.add_extension(authority_key, critical=False)
    csr_bld = csr_bld.add_extension(sans, critical=False)

    # lookup hash type (from hashes module) from name string
    hash_type = lookup_hash(ssl_csr.digest)

    # generate the csr
    csr = csr_bld.sign(key, hash_type)

    # serialize to PEM
    csr_pem = csr.public_bytes(encoding=serialization.Encoding.PEM)

    return (csr, csr_pem)
