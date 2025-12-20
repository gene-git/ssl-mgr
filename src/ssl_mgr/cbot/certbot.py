# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
load certbot config
"""
# pylint: disable=invalid-name, too-many-instance-attributes
# pylint: disable=too-few-public-methods
# import os

# from crypto_base import (SslCsr)
# from ca_sign import (CACertbot)

# from .sign_cert import certbot_sign_cert
# from .cleanup_http import cleanup_hook_http
# from .cleanup_dns import cleanup_hook_dns
from .certbothook import CertbotHook


class Certbot(CertbotHook):
    """
    Used by ssl-mgr
    """
