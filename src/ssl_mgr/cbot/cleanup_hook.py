# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
certbot cleanup hook
 - http push to web server
 - dns - accumulate till have domains for this cert
"""
from .cleanup_http import cleanup_hook_http
from .cleanup_dns import cleanup_hook_dns
from .certbothook_data import CertbotHookData


def cleanup_hook(certbot: CertbotHookData):
    """
    Clean
     - remove http token validation files
     - remove dns acme_chellenge TXT records and push dns
    """
    token = certbot.env.token
    if token:
        certbot.challenge_proto = 'http'
        cleanup_hook_http(certbot)
    else:
        certbot.challenge_proto = 'dns'
        cleanup_hook_dns(certbot)
