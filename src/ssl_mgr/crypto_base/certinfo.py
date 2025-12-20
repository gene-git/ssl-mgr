# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
# pylint: disable=too-many-instance-attributes, too-few-public-methods
# pylint: disable=invalid-name
"""
Convenient info about keys, certs and csrs
"""
from collections.abc import (Callable)

from .certinfo_data import CertInfoData
from .certinfo_print import certinfo_print


class CertInfo(CertInfoData):
    """
    Data for CertInfo.

    Used to display information about certificates,
    keys and certificate signing requests.
    """
    def print(self, print_func: Callable[..., None]):
        """
        Display what we have using provided
        log/print function.
        """
        certinfo_print(self, print_func)
