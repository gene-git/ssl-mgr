#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certificate Managerment Tools
- Read cert.pem from provided directory
- Generate the DANE TLSA "hash"
  - using openssl
  - using internal module
- check both results match.
- display result.
-
- Hardcoded to usage, selector, mathc = 3 1 1 (in practice thats all thats used)
"""
# pylint: disable=invalid-name
# pylint: disable=duplicate-code
import os
import sys
import subprocess

from ssl_mgr.crypto_base import read_cert_pem
from ssl_mgr.crypto_hash import pubkey_hash


def _help():
    """
    usage
    """
    me = sys.argv[0]
    print(f'{me} [-h] [directory containing cert.pem file(s)]')
    print('  Reads cert.pem from directory')
    print('  Generate DANE TLSA Hash directly and using openssl')
    print('  Displays result ')


def _options() -> str:
    """
    If "-s" then summary => True
    All remaining args are passed back
    in argv (or None)
    Returns
        tuple(summary: bool, argv: list[str])
    """
    cert_dir: str = './'
    argv: list[str] = []
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-h', '--help'):
            _help()
            sys.exit()

        argv = sys.argv[1:]

    if len(argv) > 0:
        cert_dir = argv[0]

    cert_file = os.path.join(cert_dir, 'cert.pem')
    if not os.path.isfile(cert_file):
        print(f'Error: Missing cert file : {cert_file}')
        sys.exit()

    return cert_dir


def _openssl_hash(cert_dir: str) -> str:
    """
    Use openssl to generate the tlsa hash (sha256 of public key)
    openssl x509 -in <cert>  -pubkey -noout | \
            openssl pkey -pubin -outform der | \
            openssl dgst -sha256
    """
    # pylint: disable=consider-using-with
    tlsa_hash: str = ''

    cert_file = os.path.join(cert_dir, 'cert.pem')
    pargs_1 = ['/usr/bin/openssl', 'x509', '-in', cert_file, '-pubkey', '-noout']
    pargs_2 = ['/usr/bin/openssl', 'pkey', '-pubin', '-outform', 'der']
    pargs_3 = ['/usr/bin/openssl', 'dgst', '-sha256']

    proc_1 = subprocess.Popen(pargs_1, stdout=subprocess.PIPE)
    if not proc_1:
        return tlsa_hash

    proc_2 = subprocess.Popen(pargs_2, stdin=proc_1.stdout, stdout=subprocess.PIPE)
    if not proc_2:
        return tlsa_hash

    proc_3 = subprocess.Popen(pargs_3, stdin=proc_2.stdout, stdout=subprocess.PIPE)
    if not proc_3:
        return tlsa_hash

    # Allow proc_1, proc_2 to receive SIGPIPE if proc_3 exits early
    if proc_1 and proc_1.stdout:
        proc_1.stdout.close()

    if proc_2 and proc_2.stdout:
        proc_2.stdout.close()

    # Get the final output
    (output, error) = proc_3.communicate()
    if error:
        print('** Error: openssl error:')
        print(error.decode() + '\n')
        return tlsa_hash

    if not output:
        return tlsa_hash

    parts = output.decode().partition('=')
    tlsa_hash = parts[2].strip()

    return tlsa_hash


def _tlsa_hash(cert_dir: str) -> str:
    """
    Get the TLSA Hash using internal modules
    """
    tlsa_hash: str = ''
    cert_data = read_cert_pem(cert_dir)
    if not cert_data:
        return tlsa_hash

    hash_type: str = 'SHA256'
    serialize_fmt: str = "DER"

    tlsa_hash = pubkey_hash(cert_data, hash_type, serialize_fmt=serialize_fmt)
    return tlsa_hash


def main():
    """
    TLSA Hash Checker
    """
    cert_dir = _options()

    tlsa_hash = _tlsa_hash(cert_dir)

    openssl_hash = _openssl_hash(cert_dir)

    if tlsa_hash != openssl_hash:
        print('** Warning: Mismatched:')
        print(f' internal: {tlsa_hash}')
        print(f'  openssl: {openssl_hash}')
    else:
        print('Matched:')
        print(f'tlsa hash: {tlsa_hash}')


if __name__ == '__main__':
    main()
