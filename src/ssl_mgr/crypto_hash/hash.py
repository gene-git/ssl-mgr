# SPDX-License-Identtifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certificate Hash
"""
from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.hashes import HashAlgorithm
# from cryptography.hazmat.primitives.hashes import HashContext
from cryptography.exceptions import UnsupportedAlgorithm

#
#
# sign only supports:
#       SHA224 | SHA256 | SHA384 | SHA512
#       | SHA3_224 | SHA3_256 | SHA3_384 | SHA3_512
# So we will only support these as well.
# So drop:
# SHAKE128 | SHAKE256 | MD5 | BLAKE2b | BLAKE2s SHA512_224 | SHA512_256
#
type HashAlgo = (
                 hashes.SHA224 |
                 hashes.SHA256 |
                 hashes.SHA384 |
                 hashes.SHA512 |
                 hashes.SHA3_224 |
                 hashes.SHA3_256 |
                 hashes.SHA3_384 |
                 hashes.SHA3_512
                 )


def lookup_hash_algo(hash_name: str) -> HashAlgo:
    """
     hash type string mapped to hashes.xxx()
     e.g.
        sha384 => hashes.SHA384()
    NB: SM3 is a CN govt hash and unsupported by hashlib or us
    replaces lookup_hash()
    """
    # pylint: disable=too-many-return-statements
    if not hash_name:
        return hashes.SHA256()

    match hash_name.upper():
        case 'SHA224': return hashes.SHA224()
        case 'SHA256': return hashes.SHA256()
        case 'SHA384': return hashes.SHA384()
        case 'SHA512': return hashes.SHA512()
        case 'SHA3_224': return hashes.SHA3_224()
        case 'SHA3_256': return hashes.SHA3_256()
        case 'SHA3_384': return hashes.SHA3_384()
        case 'SHA3_512': return hashes.SHA3_512()
        case _: return hashes.SHA256()
    return hashes.SHA256()


def make_hash(data: bytes, hash_algo: HashAlgo) -> bytes:
    """
    Make hash
    """
    try:
        digest = hashes.Hash(hash_algo)

    except UnsupportedAlgorithm:
        # should not happen
        digest = hashes.Hash(hashes.SHA256())

    digest.update(data)
    hashbytes = digest.finalize()
    return hashbytes
