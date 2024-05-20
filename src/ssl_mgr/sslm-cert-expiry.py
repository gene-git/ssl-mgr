#!/usr/bin/python
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Managerment Tools
 - Read cert pem file
 - show if certificate is expiring
"""
# pylint: disable=invalid-name
import sys
from certs import read_cert, cert_time_to_expire

def _parse_args():
    """
    Read into buffer
    """
    cert_files = None
    if len(sys.argv) > 1:
        cert_files = sys.argv[1:]
    return cert_files

def main():
    """
    Cert expiration check.
    1 arg - cert file.
    """
    cert_files = _parse_args()
    if not cert_files:
        print('Missing cert_file argument')
        return

    max_days = 30
    for file in cert_files:
        cert = read_cert(file)
        if not cert:
            print(f'Not a cert : {file}')
            continue

        (date_str, days_left) = cert_time_to_expire(cert)
        renew = 'no'
        if days_left < max_days:
            renew = 'yes'
        print(f'{file} Expires={date_str} ({days_left} days) -> Renew={renew}')

# -----------------------------------------------------
if __name__ == '__main__':
    main()
# -------------------- All Done ------------------------
