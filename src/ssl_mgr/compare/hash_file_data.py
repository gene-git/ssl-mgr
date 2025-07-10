# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
hash of contents of file
"""
import os

from utils import open_file
from crypto_hash import (lookup_hash_algo, make_hash)


def hash_file_data(fpath: str, comment_char: str = '') -> str:
    """
    Compute hash of contents of a text file.

    White space and lines starting with comment_char are removed.

    Args:
        fpath (str):
            path of file to hash

        comment_char (str):
            If non empty, then
            lines starting with this character
            are removed before hashing.
            Defaults to empty

    Returns:
        hash (str):
        hash data from file.
        If no such file, then retrusn empty string.

    We use sha3_224 - sha256 would likely be fine too.
    For dns files (like tlsa.rr) use comment_char = ';'
    Note - comments here are lines beginning with the comment char.
    Comments at end of line are left alone.
    """
    hash_str = ''

    # no input
    if not fpath:
        return hash_str

    if not os.path.isfile(fpath):
        return hash_str

    # read file if exists
    fob = open_file(fpath, 'r')
    if not fob:
        return hash_str

    rows = fob.readlines()
    fob.close()

    #
    # Data stripped and optionally no comment lines
    #
    data = ''
    for row in rows:
        row_stripped = row.strip()

        if row_stripped == '':
            continue

        if comment_char and row_stripped.startswith(comment_char):
            continue

        data += row_stripped + '\n'

    # If data is non-empty then hash it
    if data:
        bdata = data.encode()
        hash_algo = lookup_hash_algo('sha3-224')
        bhash = make_hash(bdata, hash_algo)
        hash_str = bhash.hex()

    return hash_str
