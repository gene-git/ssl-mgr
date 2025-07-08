# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Hash
"""
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509 import load_pem_x509_csr

# from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from .hash import (lookup_hash_algo, make_hash)


def cert_hash(cert_pem: bytes, hash_type: str) -> str:
    """
    Generate hash of certificate and return hex string
    Input cert_pem in bytes - if change to str then .encode() back to bytes
    """
    if not cert_pem:
        return ''

    cert = load_pem_x509_certificate(cert_pem)

    if hash_type:
        hash_algo = lookup_hash_algo(hash_type)
        cert_fingerpr = cert.fingerprint(hash_algo)
        cert_hex_str = cert_fingerpr.hex()
    else:
        encoding = serialization.Encoding.DER
        cert_bytes = cert.public_bytes(encoding)
        cert_hex_str = cert_bytes.hex()

    return cert_hex_str


def csr_hash(csr_pem: bytes, hash_type: str) -> str:
    """
    Generate a hash of CSR and return hex string
    NB csr does not have a fingerprint method so we hash
    it ourselves.
    """
    if not csr_pem:
        return ''

    csr = load_pem_x509_csr(csr_pem)
    csr_bytes = csr.public_bytes(serialization.Encoding.DER)

    hash_algo = lookup_hash_algo(hash_type)
    csr_hash_bytes = make_hash(csr_bytes, hash_algo)
    csr_hash_hex_str = csr_hash_bytes.hex()

    return csr_hash_hex_str


def pubkey_hash(cert_pem: bytes, hash_type: str,
                serialize_fmt: str = "DER") -> str:
    """
    Generate hash of pubkey in certificate and return hex string
      pubkey is serialized into DER format for TLSA
    """
    if not cert_pem:
        return ''

    cert = load_pem_x509_certificate(cert_pem)
    pub_key = cert.public_key()

    if serialize_fmt == "DER":
        encoding = serialization.Encoding.DER
    else:
        encoding = serialization.Encoding.PEM
    format_keyinfo = serialization.PublicFormat.SubjectPublicKeyInfo

    pub_key_bytes = pub_key.public_bytes(encoding=encoding,
                                         format=format_keyinfo)

    if hash_type:
        hash_algo = lookup_hash_algo(hash_type)
        pub_key_hash = make_hash(pub_key_bytes, hash_algo)
        pub_key_hex_str = pub_key_hash.hex()
    else:
        pub_key_hex_str = pub_key_bytes.hex()

    return pub_key_hex_str
