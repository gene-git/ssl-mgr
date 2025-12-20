#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certificate Managerment Tools
- Take directory on command line in which cert.pem and chain.pem reside
"""
# pylint: disable=invalid-name
import os
import sys

from crypto_cert import (cert_verify_file)
from crypto_base import (CertInfo, cert_info_from_pem_string)
from utils import read_pem


def _help():
    """
    usage
    """
    me = sys.argv[0]
    print(f'{me} [-h] <dir with cert/chain pem files>')
    print('  Verify cert using public key from chain.')


def _options() -> tuple[str, str]:
    """
    If "-s" then summary => True
    All remaining args are passed back
    in argv (or None)
    Returns
      (cert_file: str, chain_file: str)
    """
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-h', '--help'):
            _help()
            sys.exit()

        cert_dir = sys.argv[1]
        if not os.path.isdir(cert_dir):
            if os.path.isfile(cert_dir):
                cert_dir = os.path.dirname(cert_dir)
    else:
        _help()
        sys.exit()

    cert_file = ''
    chain_file = ''
    if cert_dir:
        cert_file = os.path.join(cert_dir, 'cert.pem')
        chain_file = os.path.join(cert_dir, 'chain.pem')

        if not (os.path.isfile(cert_file) and os.path.isfile(chain_file)):
            cert_file = ''
            chain_file = ''

    if not (cert_file and chain_file):
        print(f'Failed to find cert.pem, chain.pem given {cert_dir}')
        sys.exit()

    return (cert_file, chain_file)


def _print_cert_infos(cert_infos: list[CertInfo]):
    """
    Print List of cert info
    """
    for info in cert_infos:
        info.print(print)
        print('')


def read_pem_string(fpath: str) -> str:
    """
    read in as string
    """
    cert_dir = os.path.dirname(fpath)
    cert_file = os.path.basename(fpath)
    cert_bytes = read_pem(cert_dir, cert_file)
    cert_string = cert_bytes.decode()
    return cert_string


def main():
    """
    Certificate manager
    """
    (cert_file, chain_file) = _options()
    (verified, msg) = cert_verify_file(cert_file, chain_file)
    print('-------------------')
    if verified:
        print('\tCertificate ** Verified **')
    else:
        print('\tCertificate ** Failed **')
        print(msg)

    #
    # Info on cert
    #
    print('Certificate Info:')
    pem = read_pem_string(cert_file)
    cert_infos = cert_info_from_pem_string(pem)
    _print_cert_infos(cert_infos)

    print('\n-------------------')
    print('Chain Info:')
    pem = read_pem_string(chain_file)
    cert_infos = cert_info_from_pem_string(pem)
    _print_cert_infos(cert_infos)


# -----------------------------------------------------
if __name__ == '__main__':
    main()
