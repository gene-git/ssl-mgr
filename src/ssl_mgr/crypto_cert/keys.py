#!/usr/bin/python
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Crypto primative - keys
"""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import NoEncryption
from cryptography.hazmat.primitives.serialization import PrivateFormat
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from cryptography.exceptions import UnsupportedAlgorithm


def gen_key_rsa(bits: int = 2048) -> bytes:
    """
    Generate PEM encoded RSA key.

    :param int bits: Number of bits if key_type=rsa. At least 1024 for RSA.
    :returns: new RSA key in PEM form with specified number of bits
    :rtype: str
    """
    if bits < 2048:
        print(f'RSA key length : {bits} must be >= 2048')
        return b''

    expon = 65537
    try:
        key = rsa.generate_private_key(public_exponent=expon, key_size=bits)
    except (ValueError, TypeError, UnsupportedAlgorithm) as exc:
        txt = f'expon={expon} bits={bits} : {exc}'
        print(f'Failed to generate RSA key : {txt}')
        return b''

    key_pem = key.private_bytes(encoding=Encoding.PEM,
                                format=PrivateFormat.PKCS8,
                                encryption_algorithm=NoEncryption())
    return key_pem


def gen_key_ec(elliptic_curve: str = '') -> bytes:
    """
    Generate PEM encoded EC key.
    :param str elliptic_curve: The elliptic curve to use.

    :returns: new ECDSA key in PEM format of type ec_curve
    :rtype: str
    """
    try:
        curve_name = elliptic_curve.upper()
        curve = getattr(ec, curve_name)
        if not curve:
            print(f"Invalid curve : {elliptic_curve}")
            return b''

        key = ec.generate_private_key(curve=curve(), backend=default_backend())

    except TypeError as exc:
        txt = f'{elliptic_curve} : {exc}'
        print(f'Unsupported elliptic curve: {txt}')
        return b''

    except UnsupportedAlgorithm as exc:
        print(f'Unsupported Algo : {exc}')
        return b''

    key_pem = key.private_bytes(encoding=Encoding.PEM,
                                format=PrivateFormat.PKCS8,
                                encryption_algorithm=NoEncryption())
    return key_pem


def priv_to_pub_key(key_pem: bytes) -> bytes:
    """
    Returns public key associated with private key
    """
    try:
        key = load_pem_private_key(key_pem, password=None)
    except (ValueError, TypeError, UnsupportedAlgorithm) as exc:
        print(f'Failed to load private key PEM data : {exc}')
        return b''

    pubkey = key.public_key()
    pubkey_pem = pubkey.public_bytes(encoding=Encoding.PEM,
                                     format=PublicFormat.SubjectPublicKeyInfo)

    # _pkey = crypto.load_privatekey(file_type, key_pem, _passphrase)
    # _key_pem = crypto.dump_publickey(crypto.FILETYPE_PEM, _pkey)

    return pubkey_pem
