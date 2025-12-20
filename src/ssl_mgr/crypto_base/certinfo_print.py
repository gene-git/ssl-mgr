# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Print cert info
"""
from collections.abc import (Callable)

from .certinfo_data import CertInfoData


def _sans_format(sans: list[str], max_width: int, leader: str) -> str:
    """
    Break up long sans into multiple lines
    All but first line have leader in front
    """
    if not sans:
        return ''

    san_fmt = ''
    this_width = 0
    for item in sans:
        this_width += len(item)
        if this_width > max_width:
            san_fmt += '\n' + leader + item + ', '
            this_width = 0
        else:
            san_fmt += item + ', '

    return san_fmt


def certinfo_print(info: CertInfoData, log: Callable[..., None] = print):
    """
    display content of certinfo
    """
    if not info:
        return

    if info.expiry_date_str:
        log(f'Expires  : {info.expiry_date_str} ({info.expiry_string})')

    if info.issue_date_str:
        log(f'Issued   : {info.issue_date_str} ({info.issue_string})')

    if info.issuer_rfc4514:
        log(f'Issuer   : {info.issuer_rfc4514}')

    if info.subject_rfc4514:
        log(f'Subject  : {info.subject_rfc4514}')

    if info.sans:
        leader = 11 * ' '
        san_fmt = _sans_format(info.sans, 60, leader)
        log(f'Sans     : {san_fmt}')

    if info.pubkey_info:
        log(f'Pubkey   : {info.pubkey_info}')

    if info.sig_algo:
        log(f'Sig algo : {info.sig_algo}')

    # if info.sig_hash:
    #     print(f'Sig hash : {info.sig_hash}')

    if info.key_algo_str:
        log(f'Key algo : {info.key_algo_str}')
