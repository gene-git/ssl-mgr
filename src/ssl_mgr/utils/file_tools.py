# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
 file utils
"""
from typing import (Any)
import os
import stat
import tempfile
from .read_write import open_file
from .toml import dict_to_toml_string


def save_prev_symlink(fdir: str, orig: str):
    """
    If link exists rename to orig.prev
    If not a link then move to unique subdir
        fdir/fname -> fdir/saved.xxx/fname
    """
    if os.path.exists(orig):
        if os.path.islink(orig):
            saved = f'{orig}.prev'
        else:
            save_dir = tempfile.mkdtemp(suffix='', prefix='Saved', dir=fdir)
            basefile = os.path.basename(orig)
            saved = os.path.join(save_dir, basefile)
        os.rename(orig, saved)


def make_symlink(target: str, linkname: str):
    """
    file_symlink(target, linkname)
    Does equivalent to:  ln -s target linkname
    """
    done = False
    #
    # check if its there and correct
    # If there but wrong, remove the old link
    #
    if os.path.islink(linkname):
        targ = os.readlink(linkname)
        if targ == target:
            done = True
        else:
            os.unlink(linkname)

    if not done:
        os.symlink(target, linkname)


def write_conf_file(header: str, data_dict: dict[str, Any], path: str):
    """
    Write config file - header at top and data follows
     - set perms to user,group = RW
    """
    file_perm = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP

    okay = True
    fobj = open_file(path, 'w')
    if fobj:
        fobj.write(header)
        conf_str = dict_to_toml_string(data_dict)
        fobj.write(conf_str)
    else:
        print(f'Failed to write {path}')
        okay = False

    # don't need exception check as we successfully created file above.
    os.chmod(path, file_perm)
    return okay


def os_scandir(tdir: str):
    """
    wrapper around scandir to handle exceptions
    """
    scan = None
    if os.path.exists(tdir) and os.path.isdir(tdir):
        try:
            scan = os.scandir(tdir)
        except OSError as _error:
            scan = None
    return scan


def dir_list(indir: str, path_type: str = 'name') -> list[list[str]]:
    """
    Get a list of files in a local directory
    returns a list of files/dirs/links in a directory
    path_type - 'name' returns filename, 'path' returns the 'path'
    [flist, dlist, llist]
        flist = list of files
        dlist = list of dirds
        llist = list of links
    NB order care needed - symlinks are also files or dirs -
    so always check link before file or dir as we want links separated
    whether or not they point to a dir or file.
    """
    flist = []
    dlist = []
    llist = []

    scan = os_scandir(indir)
    if scan:
        for item in scan:
            file = item.name
            if path_type == 'path':
                file = item.path

            if item.is_symlink():
                llist.append(file)

            elif item.is_file():
                flist.append(file)

            elif item.is_dir():
                dlist.append(file)
        scan.close()
    return [flist, dlist, llist]


def os_chmod(path: str, perm: int) -> bool:
    """
    os.chmod with exception check
     - returns True/False if all okay/not okay
    """
    okay = True
    try:
        os.chmod(path, perm)
    except OSError:
        okay = False

    return okay


def set_restictive_file_perms(topdir: str, strict_dir: bool = False) -> bool:
    """
    Restrict permissions recursively
        user = rwX
        group = rX
        other = (if strict_dir False, then directories allow o=rX)
     where X means x if a dir
     Return True unless any os.chmod() throws exception
    """
    okay = True

    if not (os.path.exists(topdir) and os.path.isdir(topdir)):
        return okay

    file_perm_x = stat.S_IRWXU | stat.S_IXGRP | stat.S_IRGRP
    file_perm = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP
    dir_perm = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP
    if not strict_dir:
        # allow o=rx for non-strict directories
        dir_perm |= stat.S_IROTH | stat.S_IXOTH

    is_ok = os_chmod(topdir, dir_perm)
    if not is_ok:
        okay = False

    for (root, dirs, files) in os.walk(topdir):
        # directories
        for this_dir in dirs:
            this_path = os.path.join(root, this_dir)
            if os.path.islink(this_path):
                continue

            is_ok = os_chmod(this_path, dir_perm)
            if not is_ok:
                okay = False

        # files
        for this_file in files:
            this_path = os.path.join(root, this_file)
            if os.path.islink(this_path):
                continue

            # keep existing executable
            perms = file_perm
            if os.access(this_path, os.X_OK):
                perms = file_perm_x
            is_ok = os_chmod(this_path, perms)
            if not is_ok:
                okay = False
    return okay


def make_dir_path(path_dir: str) -> bool:
    """
    makes directory and any missing path components
      - set reasonable permissions (owner / group)
    """
    okay = True
    dirmode = stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP
    try:
        os.makedirs(path_dir, exist_ok=True)
        os.chmod(path_dir, dirmode)
    except OSError as _error:
        okay = False
    return okay


def touch(path: str) -> bool:
    """
    If path not existing, create it,
    Othwewise update with current time
    """
    if not os.path.exists(path):
        fob = open_file(path, 'w')
        if not fob:
            print(f'Failed to create {path}')
            return False
        fob.close()
    else:
        try:
            os.utime(path)
        except OSError as err:
            print(f'Failed to touch {path}: {err}')
            return False
    return True


def rename_backup(fpath: str, ext: str) -> bool:
    """
    Rename file fpath => fpath.ext
    Any existing fpath.ext is removed
    """
    if not fpath:
        return False

    if not ext:
        print('Error: rename_backup {fpath} missing ext')
        return False

    backup = f'{fpath}{ext}'
    if os.path.exists(backup):
        try:
            os.unlink(backup)
        except OSError as err:
            print(f'Failed to unlink {backup}: {err}')
            return False
    try:
        os.rename(fpath, backup)
    except OSError as err:
        print(f'Failed to rename {fpath} to {backup}: {err}')
        return False

    return True


def get_file_time_ns(fpath: str) -> int:
    """
    Return mtime of fpath in nanosecs
    If file not found return None
    """
    try:
        fstat = os.stat(fpath)
    except OSError:
        return -1

    return fstat.st_mtime_ns
