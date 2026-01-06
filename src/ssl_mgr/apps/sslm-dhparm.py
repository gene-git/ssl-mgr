#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>

"""
Generate diffie hellman params
"""
# pylint: disable=invalid-name,duplicate-code,too-many-instance-attributes
from typing import (Any)
import os
import sys
import time
from dataclasses import dataclass, field
import argparse

from ssl_mgr.utils import dir_list, make_dir_path, make_symlink
from ssl_mgr.utils import get_file_time_ns
from ssl_mgr.crypto_dhparm import (named_dh_params_file, new_dh_params_file)

type Opt = tuple[str | tuple[str, str], dict[str, Any]]


@dataclass
class DhOpts:
    """ options """
    force: bool = False
    age_days: int = 120
    keys: str = ''
    keylist: list[int] = field(default_factory=list)
    sizes: list[int] = field(default_factory=list)
    named: list[str] = field(default_factory=list)
    subdirs: bool = False
    dirs_in: list[str] = field(default_factory=list)
    topdirs: list[str] = field(default_factory=list)


def _dh_filename(name: int | str) -> str:
    """
    return filename of one param file
    """
    if isinstance(name, int):
        filename = f'dh{name}.pem'
    else:
        filename = f'dh-{name}.pem'

    return filename


def _get_keysizes_todo(now_ns: int, dh_opts: DhOpts, dh_dir: str
                       ) -> tuple[list[str], list[int]]:
    """
    Check each key size file
    If missing or older than min age then add to list
    Return list of keysizes that need updating
    """
    if dh_opts.force:
        return (dh_opts.named, dh_opts.sizes)

    #
    # get the age bogey in ns
    #
    min_age_days = dh_opts.age_days
    min_ns = min_age_days * 24 * 60 * 60 * 1_000_000_000

    sizes_todo = []
    for keysize in dh_opts.sizes:
        filename = _dh_filename(keysize)
        fpath = os.path.join(dh_dir, filename)
        file_time_ns = get_file_time_ns(fpath)
        if not file_time_ns:
            # missing keysize file
            sizes_todo.append(keysize)
            continue

        # found file - check the age
        file_age_ns = now_ns - file_time_ns
        if file_age_ns > min_ns:
            sizes_todo.append(keysize)

    named_todo = []
    for name in dh_opts.named:
        filename = _dh_filename(name)
        fpath = os.path.join(dh_dir, filename)
        if not os.path.exists(fpath):
            named_todo.append(name)

    return (named_todo, sizes_todo)


def _gen_keylist(key_str: str) -> tuple[list[int], list[str], list[int]]:
    """
    make 2 lists out of csv list
     - named groups and key sizes to generate
     - first item in keylist is the default symnlink dhparm.pem
    """
    keylist: list[int] = []
    named_groups: list[str] = []
    sizes: list[int] = []

    named_groups = ['ffdhe8192', 'ffdhe6144', 'ffdhe4096']
    if not key_str:
        return (keylist, named_groups, [])

    for item in key_str.split(','):
        if item.isnumeric():
            keylist.append(int(item))
            sizes.append(int(item))
        else:
            # keylist.append(item)
            named_groups.append(item)

    return (keylist, named_groups, sizes)


def _get_subdirs(topdir: str) -> list[str]:
    """
    Make list of sub-directories to put dhparms in
    Since these are domains we ignore if named "ca"
    Returns list of [topdir/subdir]
    """
    subdirs: list[str] = []
    if not topdir:
        return subdirs

    (_fls, dirs, _lnks) = dir_list(topdir, path_type='name')
    if dirs:
        for subdir in dirs:
            if subdir.lower() != 'ca':
                subdir_path = os.path.join(topdir, subdir)
                subdirs.append(subdir_path)
    if not subdirs:
        print(f'No domain subdirs found in {topdir}')
    return subdirs


def _check_input_dirs(dirs_in) -> list[str]:
    """
    Check dirs provided are directories - skip any if not
    Since these are user input we allow any name including 'ca'
    """
    dirs: list[str] = []
    if not dirs_in:
        return dirs

    for this_dir in dirs_in:
        if os.path.isdir(this_dir):
            dirs.append(this_dir)
        else:
            print(f'Warning : no such directory: {this_dir} - ignoring')
    return dirs


def _get_options() -> DhOpts:
    """
    Options
    """
    opts: list[Opt] = []

    keys = 'ffdhe8192,ffdhe6144,ffdhe4096,ffdhe3072,ffdhe2048'
    ohelp = 'Comma sep list of pre-defined names or key sizes'
    ohelp += f', first used as default ({keys})'
    opts.append((('-k', '--keys'),
                 {'help': ohelp,
                  'default': keys}
                 ))

    opts.append((('-f', '--force'),
                 {'help': 'Force update on',
                  'action': 'store_true'}
                 ))

    age_days = 120
    ohelp = f'File Age (days) before gets updated ({age_days})'
    opts.append((('-a', '--age-days'),
                 {'help': ohelp,
                  'default': age_days}
                 ))

    ohelp = 'Create parms in subdirs of input direcory ignore "ca"'
    opts.append((('-s', '--subdirs'),
                 {'help': ohelp,
                  'action': 'store_true'}
                 ))

    ohelp = 'One or more directories where parms are created'
    ohelp += ' (or their subdirs if set)'
    opts.append((('dirs_in'),
                 {'help': ohelp,
                  'nargs': '+'}
                 ))

    #
    # Install the options into parser
    #
    par = argparse.ArgumentParser(description='Diffie Helman Parameters')

    for opt in opts:
        opt_list, kwargs = opt
        if isinstance(opt_list, str):
            par.add_argument(opt_list, **kwargs)
        else:
            par.add_argument(*opt_list, **kwargs)

    #
    # Save options into DhOpts
    #
    dh_opts = DhOpts()
    parsed = par.parse_args(sys.argv[1:])
    if parsed:
        for (key, val) in vars(parsed).items():
            if key == 'age_days':
                setattr(dh_opts, key, int(val))
            else:
                setattr(dh_opts, key, val)

    #
    # Make list of all and separate lists for named and sizes
    #
    (keylist, named, sizes) = _gen_keylist(dh_opts.keys)
    dh_opts.keylist = keylist
    dh_opts.named = named
    dh_opts.sizes = sizes

    #
    # Make sure input directories exist
    #
    dh_opts.topdirs = _check_input_dirs(dh_opts.dirs_in)

    if not dh_opts.topdirs:
        print('No usable directories')
    return dh_opts


def main():
    """
    Generate dh parm files in list of one or more directories
    or (with -s) in subdirs of those dirs. When scanning for subdirs, 'ca' is
    ignored

    Key sizes default to 4096,2048 with first being the default (symlinked)
    Use -k to specify key sizes
    Only files older than 120 days (or missing) will be generated.
    Typical usage is in cron:
    sslmg-dhparm -s /etc/ssl-mgr/prod-certs
    Under prod-certs are apex domains and thus dh param
    files will be created in /etc/ssl-mgr/prod-certs/<apex-domain>/dh/
    """
    dh_opts = _get_options()
    now_ns = time.time_ns()

    #
    # Process each domain:
    #
    for topdir in dh_opts.topdirs:
        print(f' dhparam : {topdir}')
        if dh_opts.subdirs:
            subdirs = _get_subdirs(topdir)
        else:
            subdirs = [topdir]

        for subdir in subdirs:
            dh_dir = os.path.join(subdir, 'dh')
            print(f'{":":>10s} {dh_dir}')
            make_dir_path(dh_dir)

            # check file age (of default)
            (named, sizes) = _get_keysizes_todo(now_ns, dh_opts, dh_dir)
            for name in named:
                # generte named param file
                print(f'{"-":>12s} {name}')
                named_dh_params_file(name, dh_dir)

            for key_size in sizes:
                # generate new dh param file
                print(f'{"-":>12s} {key_size}')
                new_dh_params_file(key_size, dh_dir)

            if named or sizes:
                #
                # If any updated, set sym link to first.
                #
                default = dh_opts.keylist[0]
                dhfile = _dh_filename(default)
                linkname = os.path.join(dh_dir, 'dhparam.pem')
                print(f'{"":12s} default {linkname} -> {dhfile}')
                make_symlink(dhfile, linkname)


if __name__ == '__main__':
    main()
