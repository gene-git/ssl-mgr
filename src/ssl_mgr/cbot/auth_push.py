# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Auth push
"""
from .auth_push_dns import auth_push_dns
from .auth_push_http import auth_push_http

def auth_push(certbot:'CertbotHook', auth_data_rows:[str]) -> None:
    """
    Push acme validation
    Input : list of validations strings 
    Push back to certbot for validation via:
    http or rdns
    """
    certbot.log(f'auth_push acme: {certbot.challenge_proto}', opt='sdash')
    if certbot.challenge_proto == 'http':
        auth_push_http(certbot, auth_data_rows)
    else:
        auth_push_dns(certbot, auth_data_rows)
