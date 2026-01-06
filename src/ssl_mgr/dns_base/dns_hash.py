# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
hash of DNS file
"""
from ssl_mgr.compare import hash_file_data


def dns_file_hash(fpath: str) -> str:
    """
    Compute hash of a dns file
    input : fpath
        path of file to hash
    return: hash
        hash data in dns file, otherwise None
    We strip white space and dns comments (line starting with ;)
    We leave comments that are after any data.
    """
    hash_dns = hash_file_data(fpath, comment_char=';')

    return hash_dns
