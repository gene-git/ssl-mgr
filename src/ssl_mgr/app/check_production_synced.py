# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Check that production certs are same as latest "certs" output.
"""
# pylint: disable=too-many-locals
import os

from utils import dir_list
from utils import Log
from compare import compare_files

from .ssl_mgr_data import SslMgrData


class _Check:
    """
    share data
    """
    def __init__(self, mgr: SslMgrData):
        self.mgr: SslMgrData = mgr
        self.topdir: str = mgr.opts.top_dir
        self.have_cert_dir: bool = True

        self.cert_dir: str = os.path.join(self.topdir, 'certs')
        self.prod_dir: str = mgr.opts.prod_cert_dir
        self.group_names: list[str] = list(mgr.groups.keys())

        self.grps_svcs: dict[str, list[str]] = {}
        self.init_groups_services()

        if not os.path.isdir(self.cert_dir):
            self.have_cert_dir = False

    def init_groups_services(self):
        """
        Initializew group/servive names.
        """
        for gname in self.group_names:
            self.grps_svcs[gname] = self.mgr.groups[gname].svcs

    def group_names_synced(self):
        """
        Check that every group is in production.
        Note: can be unused old groups so
        we check one by one.
        """
        logger = Log()
        logs = logger.logs

        group_names_prod: list[str] = _group_list(self.prod_dir)
        for gname in self.group_names:
            if gname not in group_names_prod:
                logs(f' Mismatch: production group missing {gname}.')
                return False
        return True

    def tlsa_synced(self) -> bool:
        """
        For every <group> check :
        - <cert_dir>/<group>/tlsa.<group>
        - <prod_dir>/<group>/tlsa.<group>
        Returns True if tlsa files are all the same.
        """
        logger = Log()
        logs = logger.logs

        for gname in self.group_names:
            grp_file = os.path.join(self.cert_dir, gname, f'tlsa.{gname}')
            prd_file = os.path.join(self.prod_dir, gname, f'tlsa.{gname}')

            same = compare_files(grp_file, prd_file, comment_char=';')
            if not same:
                logs(f' Mismatch: {grp_file}')
                logs(f'   vs    : {prd_file}')
                return False
        return True

    def certs_synced(self) -> bool:
        """
        Check curr and next are in sync.
        Note in prod curr/next are real directories
        while cert_dir they are symlinks to dated
        directories.
        """
        for gname in self.group_names:
            grp_dir = os.path.join(self.cert_dir, gname)
            prd_dir = os.path.join(self.prod_dir, gname)

            service_names = self.grps_svcs[gname]

            for sname in service_names:
                same = _check_cert_dir(grp_dir, prd_dir, sname, 'curr')
                if not same:
                    return False

                same = _check_cert_dir(grp_dir, prd_dir, sname, 'next')
                if not same:
                    return False
        return True


def check_production_synced(mgr: SslMgrData):
    """
    In event of errors, it is possible that production files:
    - certs/keys/chain
    - dns dane tlsa
    Are out of sync.
    Return True if in sync else false.

    If out of sync then need to fix - suggest running:
        sslm-mgr dev --certs-to-prod --force-server-restarts
    """
    logger = Log()
    logs = logger.logs

    logs('Checking production directory is up to date.')

    # prep some data
    check = _Check(mgr)

    if not check.have_cert_dir:
        logs(' Skipped: No cert dir. Possibly a new set up.')
        return True

    # list of groups must match
    if not check.group_names_synced():
        return False

    if not check.tlsa_synced():
        return False

    if not check.certs_synced():
        return False

    return True


def _group_list(group_dir: str) -> list[str]:
    """
    Return list of groups (directories) in gdir.
    Groups are always a real directory.
    """
    (_fls, group_dirs, _lnks) = dir_list(group_dir)
    return group_dirs


def _check_cert_dir(group_dir: str, prod_dir: str, sname: str,
                    which: str) -> bool:
    """
    Check that certs and chains are in sync
    which is 'curr' or 'next'
    sname is the service name.
    """
    logger = Log()
    logs = logger.logs

    #
    # Check if dirs consistent
    #
    cdir = os.path.join(group_dir, sname, which)
    pdir = os.path.join(prod_dir, sname, which)
    cdir_exist = os.path.exists(cdir)
    pdir_exist = os.path.exists(pdir)

    # both are absent -> okay
    if not (cdir_exist or pdir_exist):
        return True

    # one absent one is not -> not okay
    if not (cdir_exist and pdir_exist):
        logs(f' Mismatch: {cdir}')
        logs(f'   vs    : {pdir}')
        return False

    # both exist - check content.
    files = ('privkey.pem', 'cert.pem', 'csr.pem', 'bundle.pem',
             'chain.pem', 'fullchain.pem')

    for file in files:
        cert_file = os.path.join(group_dir, sname, which, file)
        prod_file = os.path.join(prod_dir, sname, which, file)

        same = compare_files(cert_file, prod_file, comment_char=';')
        if not same:
            logs(f' Mismatch: {cert_file}')
            logs(f'   vs    : {prod_file}')
            return False

    return True
