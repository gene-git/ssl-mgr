# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Cert helpers
"""
import os
import stat
from pathlib import Path
from cryptography import x509
from cryptography.x509 import load_pem_x509_certificate
from utils import write_pem
from utils import read_pem
from utils import get_file_time_ns


def _restrict_file_perms(fpath: str):
    """
    Restrictive permissions
      owner = RW
      group = none
      other = none
    """
    perm = stat.S_IWUSR | stat.S_IRUSR
    try:
        os.chmod(fpath, perm)
    except OSError:
        pass


def read_privkey_pem(db_dir: str) -> bytes:
    """ read privkey pem file and return the pem """
    pemfile = 'privkey.pem'
    privkey_pem = read_pem(db_dir, pemfile)
    return privkey_pem


def save_privkey_pem(chain_pem: bytes, db_dir: str) -> bool:
    """
    Save privkey pem file into db_dir
    Set restrictive permissions.
    """
    keyname = 'privkey.pem'
    okay = write_pem(chain_pem, db_dir, keyname)
    fpath = os.path.join(db_dir, keyname)
    _restrict_file_perms(fpath)
    return okay


def save_chain_pem(chain_pem: bytes, db_dir: str) -> bool:
    """
    write out pem file into db_dir
    """
    okay = write_pem(chain_pem, db_dir, 'chain.pem')
    return okay


def save_fullchain_pem(fullchain_pem: bytes, db_dir: str) -> bool:
    """
    write out pem file into db_dir
    """
    okay = write_pem(fullchain_pem, db_dir, 'fullchain.pem')
    return okay


def save_cert_pem(cert_pem: bytes, db_dir: str) -> bool:
    """
    write out pem file into db_dir
    """
    okay = write_pem(cert_pem, db_dir, 'cert.pem')
    return okay


def read_fullchain_pem(db_dir: str) -> bytes:
    """
    Read fullchain
    """
    fullchain_pem = read_pem(db_dir, 'fullchain.pem')
    return fullchain_pem


def read_chain_pem(db_dir: str) -> bytes:
    """
    Read chain
    """
    chain_pem = read_pem(db_dir, 'chain.pem')
    return chain_pem


def read_cert_pem(db_dir: str) -> bytes:
    """
    Read cert
    """
    cert_pem = read_pem(db_dir, 'cert.pem')
    return cert_pem


def cert_file_time_ns(db_dir: str):
    """ return the cert file time in nanosecs"""
    path = os.path.join(db_dir, 'cert.pem')
    return get_file_time_ns(path)


def save_bundle(key_pem: bytes, fullchain_pem: bytes, db_dir: str) -> bool:
    """
    Save bundle = key + fullchain
    """
    filename = 'bundle.pem'
    bundle_pem = key_pem + fullchain_pem
    okay = write_pem(bundle_pem, db_dir, filename)

    fpath = os.path.join(db_dir, filename)
    _restrict_file_perms(fpath)

    return okay


def read_cert(fpath: str) -> x509.Certificate:
    """
    Read pem file and return x509.Certificate
     - fpath = full path to certificate file
    """
    path = Path(fpath)
    certname = path.name
    dirname = str(path.parents[0])

    cert_pem = read_pem(dirname, certname)
    cert = load_pem_x509_certificate(cert_pem)

    return cert
