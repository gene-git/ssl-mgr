#!/usr/bin/python
# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
# pylint: disable=invalid-name
"""
Certificate Managerment Tools
   In broad terms there are 2 types of group entities
    - CA
    - Domain
"""
from app import SslMgr


def main():
    """
    Certificate manager
    """
    ssl_mgr = SslMgr()
    okay = ssl_mgr.do_tasks()
    if not okay:
        print('Failed to perform required task(s)')


# -----------------------------------------------------
if __name__ == '__main__':
    main()
