# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
File locking
"""
import os
import sys
import pwd
import hashlib
from lockmgr import LockMgr

class SslLockMgr:
    """
    file locking
     - NEVER create more than 1 lock instance with same name.
     - if need multiple locks use different locknames
     (no longer used: 2 parts - advisory lockfile and companion pid file)
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, conf_dir:str):
        self.conf_dir = conf_dir
        self.log = print

        self.euid = os.geteuid()
        self.username = pwd.getpwuid(self.euid)[0]
        self.mypid = os.getpid()
        self.proc_name = sys.argv[0]

        #
        # Make lockdir, and hash conf_dir to make filename
        #
        lockdir = f'/tmp/sslm-mgr-lck.{self.euid}'
        os.makedirs(lockdir, exist_ok=True)

        lockname =  hashlib.sha3_224(conf_dir.encode())
        lockname = lockname.hexdigest()
        lockname = lockname[:32]
        self.lockfile = f'{lockdir}/{lockname}'

        self.lockmgr = LockMgr(self.lockfile)
        self.acquired =  self.lockmgr.acquired

    def lock_info(self):
        """ print lock info """
        attrs = ['lockfile', 'name', 'euid' ]
        for attr in attrs:
            item = getattr(self, attr)
            print(f'{attr} : {item}')

    def set_logger(self, log):
        """ use provided logger """
        self.log = log

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
