# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
# pylint: disable=too-many-instance-attributes, too-few-public-methods
# pylint: disable=invalid-name
"""
Convenient info about keys, certs and csrs
"""
from datetime import datetime, timezone

from .cert_expires import CertExpires


class CertInfoData:
    """
    Data for CertInfo.

    Used to display information about certificates,
    keys and certificate signing requests.
    """
    def __init__(self):
        #
        # Certificates and CSRs.
        # Initialize expires to unix epoch
        #
        unix_epoch = datetime.fromtimestamp(0, timezone.utc)
        self.expires: CertExpires = CertExpires(unix_epoch, unix_epoch)

        self.expiry_date_str: str = ''
        self.days_left: float = -1.0
        self.seconds_left: float = -1.0
        self.expiry_string: str = ''

        self.issue_date_str: str = ''
        self.issue_days_ago: float = -1
        self.issue_seconds_ago: float = -1
        self.issue_string: str = ''

        self.issuer_rfc4514: str = ''
        self.issuer_CN: str = ''
        self.issuer_O: str = ''
        self.subject_rfc4514: str = ''
        self.subject_CN: str = ''
        self.sans: list[str] = []
        self.pubkey_info: str = ''
        self.sig_algo: str = ''
        self.sig_hash: str = ''

        #
        # Key
        #
        self.key_algo_str: str = ''  # see key_info()
