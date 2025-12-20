# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Auth push
"""
from utils import Log

from .auth_push_dns import auth_push_dns
from .auth_push_http import auth_push_http
from .certbothook_data import CertbotHookData


def auth_push(certbot: CertbotHookData, auth_data_rows: list[str]):
    """
    Push acme validation
    Input : list of validations strings
    Push back to certbot for validation via:
    http or rdns
    """
    logger = Log()
    logger.log(f'auth_push acme: {certbot.challenge_proto}', opt='sdash')
    if certbot.challenge_proto == 'http':
        auth_push_http(certbot, auth_data_rows)
    else:
        auth_push_dns(certbot, auth_data_rows)
