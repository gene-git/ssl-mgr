# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
'''
ip address tools
'''
import ipaddress
from ipaddress import (AddressValueError, NetmaskValueError)


def is_valid_ip4(address: str) -> bool:
    ''' check if valid address or cidr '''
    try:
        _check = ipaddress.IPv4Network(address, strict=False)
        return True
    except (AddressValueError, NetmaskValueError, TypeError):
        return False


def is_valid_ip6(address: str) -> bool:
    ''' check if valid address or cidr '''
    try:
        _check = ipaddress.IPv6Network(address, strict=False)
        return True
    except (AddressValueError, NetmaskValueError, TypeError):
        return False


def is_valid_cidr(address: str) -> bool:
    '''
    check if valid ip address
     - returns True/False
    '''
    if not address:
        return False
    if is_valid_ip4(address) or is_valid_ip6(address):
        return True
    return False
