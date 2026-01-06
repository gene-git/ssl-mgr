# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
# Split this up and delegate down to group
"""
clean up unused older data from <grp>/<svc>/db/xxx
"""
# pylint: disable=too-many-locals,too-many-nested-blocks
import os
import re

from ssl_mgr.utils import dir_list
from ssl_mgr.utils import Log
from ssl_mgr.utils import remove_path

from .ssl_mgr_data import SslMgrData


def _clean_one(num_keep: int, db_dir: str, dlist: list[str]):
    """
    clean up dirs from the directory:
       db_dir = topdir/group/service/db/

    Using list of candidate directories:
       dlist
    """
    if len(dlist) <= num_keep:
        return

    logger = Log()
    log = logger.log

    # make list of paths
    plist = [os.path.join(db_dir, adir) for adir in dlist]

    # sort them newest first
    plist.sort(key=os.path.getmtime, reverse=True)
    plist = plist[num_keep:]

    log(f'Cleaning {db_dir}')
    for item in plist:
        log(f'    {item}')
        if not remove_path(item):
            log(f' Error removing {item}')


def filter_candidate_dirs(grp_dir: str, svc: str, all_cands: list[str]
                          ) -> list[str]:
    """
    Given list of candidate db directories (all_cands),
    Filter the list to those viable candidates
     - must have name in correct data format
     - must not be pointed to by symlinks curr/next/prev
    """
    logger = Log()
    log = logger.log

    #
    # DB dir names are: yyyymmdd-hh:mm:ss
    #  - regex to check right date format
    #
    dirname_re = r'^[\d]{8}\-[\d]{2}:[\d]{2}:[\d]{2}$'
    dir_re = re.compile(dirname_re)

    #
    # Get list of target dirs pointed to by curr/next/prev symlinks
    #  -> link_targs
    #
    links_to_skip = ('curr', 'next', 'prev')
    link_targs = []
    for link in links_to_skip:
        #
        # link_targ := dir pointed to by this link
        #
        link_path = os.path.join(grp_dir, svc, link)
        link_targ = None
        if os.path.islink(link_path):
            link_targ = os.readlink(link_path)
            if link_targ:
                link_dir_name = os.path.basename(link_targ)
                link_targs.append(link_dir_name)

    #
    # Filter the list
    #  - all_cands -> ok_cands
    #
    ok_cands: list[str] = []
    for cand in all_cands:
        #
        # skip any link targets
        #
        if cand in link_targs:
            continue

        #
        # skip if name not correct date format
        #
        name_format = dir_re.match(cand)
        if not name_format:
            log(f'Unexpected dir {grp_dir}/{svc}/db/{cand}')
            continue
        ok_cands.append(cand)

    return ok_cands


def cleanup(ssl_mgr: SslMgrData):
    """
    Remove old databse directories from :
       top_dir/certs/<group>/service/db/xxx

    Skip any pointed to by symlinks:
      {curr, next, prev}

    Targets
        ssl_mgr.opts.gprs_svcs
    unless do_all is set, in which case every group/service is cleaned up
    """
    top_dir = ssl_mgr.opts.top_dir
    cert_dir = os.path.join(top_dir, 'certs')
    num_keep = ssl_mgr.opts.clean_keep
    do_all = ssl_mgr.opts.clean_all

    logger = Log()
    log = logger.log

    log('Cleaning older database files')
    #
    # list of groups/services to clean
    #
    services = ssl_mgr.opts.grps_svcs
    if do_all:
        services = {}

        (_fls, grps, _lnks) = dir_list(cert_dir, path_type='path')
        for grp_path in grps:
            grp_name = os.path.basename(grp_path)

            #
            # Check known in conf.d/xxx
            #
            grp_config = os.path.join(top_dir, 'conf.d', grp_name)
            if not (os.path.exists(grp_config) or os.path.isdir(grp_config)):
                continue

            #
            # List of services for this group
            #
            [_fls, svcs, _lnks] = dir_list(grp_path, path_type='name')
            if svcs:
                services[grp_name] = svcs
    #
    # clean up each group,service pair
    #
    for (grp_name, svcs) in services.items():
        grp_dir = os.path.join(cert_dir, grp_name)
        for svc in svcs:
            db_dir = os.path.join(grp_dir, svc, 'db')

            #
            # candidates for this group/svc
            #
            candidate_dirs = []
            if os.path.isdir(db_dir):
                [_fls, possible_cands, _lnks] = dir_list(db_dir)
                if not possible_cands:
                    continue

                good_ones = filter_candidate_dirs(grp_dir, svc,
                                                  possible_cands)
                if good_ones:
                    candidate_dirs += good_ones

            _clean_one(num_keep, db_dir, candidate_dirs)
