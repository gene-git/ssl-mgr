# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
File locking
"""
import os
import sys
import pwd
from lockmgr import LockMgr

from utils import Log
from crypto_hash import (lookup_hash_algo, make_hash)


class SslLockMgr:
    """
    file locking
     - NEVER create more than 1 lock instance with same name.
     - if need multiple locks use different locknames
     (no longer used: 2 parts - advisory lockfile and companion pid file)
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, conf_dir: str):
        self.conf_dir = conf_dir

        self.euid = os.geteuid()
        self.username = pwd.getpwuid(self.euid)[0]
        self.mypid = os.getpid()
        self.proc_name = sys.argv[0]

        #
        # Make lockdir, and hash conf_dir to make filename
        #
        lockdir = f'/tmp/sslm-mgr-lck.{self.euid}'
        os.makedirs(lockdir, exist_ok=True)

        hash_algo = lookup_hash_algo('SHA3_224')
        hashbytes = make_hash(conf_dir.encode(), hash_algo)
        lockname = hashbytes.hex()[:32]
        self.lockfile = f'{lockdir}/{lockname}'

        self.lockmgr = LockMgr(self.lockfile)
        self.acquired = self.lockmgr.acquired

    def lock_info(self):
        """ print lock info """
        logger = Log()
        log = logger.log

        attrs = ['lockfile', 'name', 'euid']
        for attr in attrs:
            item = getattr(self, attr)
            log(f'{attr} : {item}')

    def acquire(self):
        """ acquire lock """
        gotit = self.lockmgr.acquire_lock(wait=True, timeout=30)
        return gotit

    def release(self):
        """ drop lock """
        self.lockmgr.release_lock()

    def get_lockfile(self):
        """ return lockfile name """
        return self.lockfile
