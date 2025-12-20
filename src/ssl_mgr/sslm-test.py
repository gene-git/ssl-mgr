#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certificate Managerment Test Renew Tool(s)
"""
# pylint: disable=invalid-name
# pylint: disable=duplicate-code
import sys
from config import SslOpts


def _help():
    """
    usage
    """
    me = sys.argv[0]
    print(f'{me} [-h] issue_expire now_expire')
    print('  Show renew decision')
    print('  issue_expire = expiration days at issue')
    print('  now_expire = expiration days no')
    sys.exit()


def _options() -> tuple[float, float]:
    """
    All remaining args are passed back
    in argv (or None)
    Returns
        tuple(summary: bool, argv: list[str])
    """
    argv: list[str] = []
    if len(sys.argv) < 3:
        _help()

    if len(sys.argv) > 1:
        if sys.argv[1] in ('-h', '--help'):
            _help()

    issue = float(sys.argv[1])
    expire = float(sys.argv[2])

    return (issue, expire)

def main():
    """
    Certificate manager
    """
    (issue, expire) = _options()

    opts = SslOpts()
    renew_info = opts.renew_info

    (ok, days_to_renew, rand_adj) = renew_info.renew_decision(issue, expire)

    print(f'issue expiry     : {round(issue, 3)}')
    print(f'expiry now       : {round(expire, 3)}')

    print(f'renew            : {ok}')
    print(f'days_to_renew    : {round(days_to_renew, 3)}')
    print(f'rand_adj         : {round(rand_adj, 3)}')

if __name__ == '__main__':
    main()
