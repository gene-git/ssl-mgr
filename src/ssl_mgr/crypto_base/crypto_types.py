# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Shared types etc
"""
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.asymmetric import ed448
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.asymmetric import x448
from cryptography.hazmat.primitives.asymmetric import dh
# from cryptography.hazmat.primitives.serialization import load_pem_private_key
# from cryptography.hazmat.primitives.serialization import load_pem_public_key


#
# sign() supports these key types only:
#  Ed25519PrivateKey | Ed448PrivateKey | RSAPrivateKey
#  | DSAPrivateKey | EllipticCurvePrivateKey
#
type KeyTypePrvOther = (
        x25519.X25519PrivateKey |
        x448.X448PrivateKey |
        dh.DHPrivateKey
        )
type KeyTypePrv = (
        ed25519.Ed25519PrivateKey |
        ed448.Ed448PrivateKey |
        rsa.RSAPrivateKey |
        dsa.DSAPrivateKey |
        ec.EllipticCurvePrivateKey
        )

type KeyTypePubOther = (
        x25519.X25519PublicKey |
        x448.X448PublicKey |
        dh.DHPublicKey
        )
type KeyTypePub = (
        ed25519.Ed25519PublicKey |
        ed448.Ed448PublicKey |
        rsa.RSAPublicKey |
        dsa.DSAPublicKey |
        ec.EllipticCurvePublicKey
        )


def valid_prvkey_type(key: KeyTypePrv | KeyTypePrvOther) -> bool:
    """
    Returns true if private key type is acceptable.

    cryptography module has some functions/classes accept many
    key types, but others (like signing) are restricted.

    We only use the subset and this checks the key is usable.
    """
    if isinstance(key, ed25519.Ed25519PrivateKey
                  | ed448.Ed448PrivateKey
                  | rsa.RSAPrivateKey
                  | dsa.DSAPrivateKey
                  | ec.EllipticCurvePrivateKey):
        return True
    return False


def valid_pubkey_type(key: KeyTypePub | KeyTypePubOther) -> bool:
    """
    Returns true if private key type is acceptable.

    cryptography module has some functions/classes accept many
    key types, but others (like signing) are restricted.

    We only use the subset and this checks the key is usable.
    """
    if isinstance(key, ed25519.Ed25519PublicKey
                  | ed448.Ed448PublicKey
                  | rsa.RSAPublicKey
                  | dsa.DSAPublicKey
                  | ec.EllipticCurvePublicKey):
        return True
    return False
