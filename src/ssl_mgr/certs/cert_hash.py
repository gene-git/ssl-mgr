# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Hash
"""
from cryptography.x509 import load_pem_x509_certificate
from cryptography.x509 import load_pem_x509_csr

#from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from .hash import lookup_hash
from .hash import lookup_hash_func

def cert_hash(cert_pem:bytes, hash_type:str) -> str :
    """
    Generate hash of certificate and return hex string
    Input cert_pem in bytes - if change to str then .encode() back to bytes
    """
    cert = load_pem_x509_certificate(cert_pem)

    if hash_type:
        hash_method = lookup_hash(hash_type)
        cert_fingerpr = cert.fingerprint(hash_method)
        cert_hex_str = cert_fingerpr.hex()
    else:
        encoding = serialization.Encoding.DER
        cert_bytes = cert.public_bytes(encoding)
        cert_hex_str = cert_bytes.hex()

    return cert_hex_str

def csr_hash(csr_pem:bytes, hash_type:str) -> str :
    """
    Generate hash of certificate and return hex string
    """
    csr = load_pem_x509_csr(csr_pem)
    hash_method = lookup_hash(hash_type)
    csr_fingerpr = csr.fingerprint(hash_method)
    csr_hash_hex_str = csr_fingerpr.hex()

    return csr_hash_hex_str

def pubkey_hash(cert_pem:bytes, hash_type:str, serialize_fmt="DER") -> str :
    """
    Generate hash of pubkey in certificate and return hex string
      pubkey is serialized into DER format for TLSA
    """
    cert = load_pem_x509_certificate(cert_pem)
    pub_key = cert.public_key()

    if serialize_fmt == "DER":
        encoding = serialization.Encoding.DER
    else:
        encoding = serialization.Encoding.PEM
    format_keyinfo = serialization.PublicFormat.SubjectPublicKeyInfo

    pub_key_bytes = pub_key.public_bytes(encoding=encoding, format=format_keyinfo)

    if hash_type:
        hash_func = lookup_hash_func(hash_type)
        pub_key_hash = hash_func(pub_key_bytes)
        pub_key_hex_str = pub_key_hash.hexdigest()
    else:
        pub_key_hex_str = pub_key_bytes.hex()

    return pub_key_hex_str
