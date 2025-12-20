# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
load certbot config
"""
# pylint disable=invalid-name, too-many-instance-attributes
# pylint disable=too-few-public-methods

from .certbothook_data import CertbotHookData
from .auth_hook import auth_hook
from .cleanup_hook import cleanup_hook


class CertbotHook(CertbotHookData):
    """
    Used by certbot hook which has less info than when loaded by ssl-mgr
    """
    def auth_hook(self):
        """
        when run as hook
        """
        result = auth_hook(self)
        return result

    def cleanup_hook(self):
        """
        when run as hook - not using cleanup hook
        """
        cleanup_hook(self)
