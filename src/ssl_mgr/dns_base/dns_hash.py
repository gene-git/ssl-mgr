# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
hash of DNS file
"""
from utils import open_file
from crypto_hash import (lookup_hash_algo, make_hash)


def dns_file_hash(fpath: str) -> str:
    """
    Compute hash of a dns file
    input : fpath
        path of file to hash
    return: hash
        hash data in dns file, otherwise None
    We strip white space and dns comments (line starting with ;)
    We leave comments that are after any data.
    We use sha3_224 - sha256 would likely be fine too.
    """
    hash_dns = ''

    # no input
    if not fpath:
        return hash_dns

    # read file if exists
    fob = open_file(fpath, 'r')
    if not fob:
        return hash_dns

    rows = fob.readlines()
    fob.close()

    #
    # data = stripped and no comment lines
    #
    data = ''
    for row in rows:
        row_stripped = row.strip()
        if row_stripped.startswith(';') or row_stripped.startswith('\n'):
            continue

        data += row_stripped + '\n'

    if data:
        bdata = data.encode()
        hash_algo = lookup_hash_algo('sha3-224')
        bhash = make_hash(bdata, hash_algo)
        hash_dns = bhash.hex()

    return hash_dns
