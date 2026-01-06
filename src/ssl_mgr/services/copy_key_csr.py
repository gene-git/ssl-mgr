# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Copy existing private key and CSR
"""
# pylint: disable=invalid-name
import os

from ssl_mgr.utils import copy_file_atomic
from ssl_mgr.utils import Log
from ssl_mgr.db import SslDb


def copy_key_csr(db: SslDb, db_src: str, db_dst: str) -> bool:
    """
    Copy private key and CSR from one database to another
    This is used to make a new 'next' but keeping the CSR
    This allows to keep the key pairs and therefore DNS DANE TLSA
    records don't change as public key is same.
    Since state is from file time we copy that too.
    """
    logger = Log()
    log = logger.log
    logs = logger.logs

    src_dir = os.path.join(db.db_dir, db_src)
    dst_dir = os.path.join(db.db_dir, db_dst)

    fnames = ('privkey.pem', 'csr.pem')

    for file in fnames:
        src_file = os.path.join(src_dir, file)
        dst_file = os.path.join(dst_dir, file)

        okay = copy_file_atomic(src_file, dst_file, log=log)
        if not okay:
            logs(f'Error: Failed to copy {src_file} -> {dst_file}')

    return True
