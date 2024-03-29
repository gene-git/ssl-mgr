# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
hash of DNS file
"""
import hashlib
from utils import open_file

def dns_file_hash(fpath):
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

    # no input
    if not fpath :
        return None

    # read file if exists
    fob = open_file(fpath, 'r')
    if not fob:
        return None

    hash_dns = None
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
        data = data.encode()
        hash_dns = hashlib.sha3_224(data)
        hash_dns = hash_dns.hexdigest()

    return hash_dns
