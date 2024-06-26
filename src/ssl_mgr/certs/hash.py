# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Hash 
"""
import hashlib
from cryptography.hazmat.primitives import hashes

def lookup_hash(hash_type:str) :
    """
     hash type string mapped to hashes.xxx()
     e.g.
        sha384 => hashes.SHA384()
    """
    if not hash_type:
        return hashes.SHA256()

    match hash_type.upper() :
        case 'SHA1':
            hash_method = hashes.SHA1()
        case 'SHA512_224':
            hash_method = hashes.SHA512_224()
        case 'SHA512_256':
            hash_method = hashes.SHA512_256()
        case 'SHA224':
            hash_method = hashes.SHA224()
        case 'SHA256':
            hash_method = hashes.SHA256()
        case 'SHA384':
            hash_method = hashes.SHA384()
        case 'SHA512':
            hash_method = hashes.SHA512()
        case 'SHA3_224':
            hash_method = hashes.SHA3_224()
        case 'SHA3_256':
            hash_method = hashes.SHA3_256()
        case 'SHA3_384':
            hash_method = hashes.SHA3_384()
        case 'SHA3_512':
            hash_method = hashes.SHA3_512()
        case 'SHAKE128':
            hash_method = hashes.SHAKE128(128)
        case 'SHAKE256':
            hash_method = hashes.SHAKE256(256)
        case 'MD5':
            hash_method = hashes.MD5()
        case 'BLAKE2b':
            hash_method = hashes.BLAKE2b(64)
        case 'BLAKE2s':
            hash_method = hashes.BLAKE2s(32)
        case 'SM3':
            hash_method = hashes.SM3()
    return hash_method

def lookup_hash_func(hash_type:str):
    """
    Returns the hashlib function for hash_type string
    """
    if not hash_type:
        return hashlib.sha256

    match hash_type.upper() :
        case 'SHA1':
            hash_func = hashlib.sha1
        case 'SHA512_224':
            hash_func = hashlib.sha512
        case 'SHA512_256':
            hash_func = hashlib.sha512
        case 'SHA224':
            hash_func = hashlib.sha224
        case 'SHA256':
            hash_func = hashlib.sha256
        case 'SHA384':
            hash_func = hashlib.sha384
        case 'SHA512':
            hash_func = hashlib.sha512
        case 'SHA3_224':
            hash_func = hashlib.sha3_224
        case 'SHA3_256':
            hash_func = hashlib.sha3_256
        case 'SHA3_384':
            hash_func = hashlib.sha3_384
        case 'SHA3_512':
            hash_func = hashlib.sha3_512
        case 'SHAKE128':
            hash_func = hashlib.shake_128
        case 'SHAKE256':
            hash_func = hashlib.shake_256
        case 'MD5':
            hash_func = hashlib.md5
        case 'BLAKE2b':
            hash_func = hashlib.blake2b
        case 'BLAKE2s':
            hash_func = hashlib.blake2s
        case 'SM3':
            # CN govt hash unsupported by hashlib or us
            hash_func = hashlib.sha256

    return hash_func
