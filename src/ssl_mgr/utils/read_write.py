# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
File tools
"""
from typing import (IO)
from collections.abc import (Callable)

import os


def open_file(path: str, mode: str, verb: bool = False) -> IO | None:
    """
    Open a file and return file object
    """
    # pylint: disable=unspecified-encoding, consider-using-with
    try:
        fobj = open(path, mode)
    except OSError as err:
        fobj = None
        if verb:
            print(f'Error opening file {path} : {err}')
    return fobj


def write_file(data: str, targ_dir: str, file: str,
               log: Callable[..., None] = print
               ) -> bool:
    """
    Write out text file
    """
    if not targ_dir:
        return False

    fpath = os.path.join(targ_dir, file)
    okay = write_path_atomic(data, fpath)
    if not okay:
        log(f'Failed to write {fpath}')
        return False
    return True


def write_path_atomic(data: str, fpath: str,
                      log: Callable[..., None] = print
                      ) -> bool:
    """
    Write data to fpath - atomic version
    """
    #
    # Create dst directories if needed
    #
    fpath_dir = os.path.dirname(fpath)
    try:
        os.makedirs(fpath_dir, exist_ok=True)
    except OSError as err:
        log(f'write_path_atomic - failed making dest dirs {fpath_dir} : {err}')
        return False

    # write temp file in same dir.
    fpath_tmp = fpath + '.tmp'
    fob = open_file(fpath_tmp, "w")
    if not fob:
        return False

    fob.write(data)
    fob.flush()
    os.fsync(fob.fileno())
    fob.close()

    # rename
    try:
        os.rename(fpath_tmp, fpath)
    except OSError as err:
        log(f'write_path_atomic - rename error {err}')
        return False
    return True


def copy_file_atomic(src: str, dst: str,
                     log: Callable[..., None] = print
                     ) -> bool:
    """
    Copy local file from src to dst
    """
    if not os.path.exists(src):
        return True

    fob = open_file(src, "r")
    if not fob:
        return False

    data = fob.read()
    fob.close()
    try:
        stat = os.stat(src)
    except OSError:
        # stat failed
        stat = None

    okay = write_path_atomic(data, dst, log=log)
    if not okay:
        return False

    # Set file time to match src
    if stat:
        os.utime(dst, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    return True


def read_file(targ_dir: str, file: str, verb: bool = False) -> str:
    """ read text file """

    if not targ_dir:
        return ''

    fpath = os.path.join(targ_dir, file)
    try:
        fobj = open_file(fpath, 'r', verb=verb)
        if not fobj:
            if verb:
                print(f'Failed to read {fpath}')
            return ''
        data = fobj.read()
        return data

    except OSError as err:
        print(f'Error with file {fpath} : {err}')
        return ''
    return ''


def copy_file(src_dir: str, file: str, targ_dir: str) -> bool:
    """
    Copy file from src_dir to targ_dir
     return True on success
    """
    spath = os.path.join(src_dir, file)
    tpath = os.path.join(targ_dir, file)
    return copy_file_atomic(spath, tpath)


def write_pem(pem: bytes, db_dir: str, file: str) -> bool:
    """
    write pem byte string to file
     - pem is bytes => decode to string
    """
    if pem:
        pem_str = pem.decode()
        is_okay = write_file(pem_str, db_dir, file)
    else:
        is_okay = False
    return is_okay


def read_pem(db_dir: str, pem_file: str) -> bytes:
    """
    read pem file and return PEM byte string
    """
    pem = b''
    pem_str = read_file(db_dir, pem_file)
    if pem_str:
        # pem = bytes(pem_str, 'utf-8')
        pem = pem_str.encode('utf-8')
    return pem
