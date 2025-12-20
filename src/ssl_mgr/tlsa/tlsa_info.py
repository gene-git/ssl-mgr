# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
TLSA data communiation class
"""
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=too-few-public-methods

from db import SslDb
from crypto_cert import SslCert
from dns_base import SslDns
from config_service import DaneTls


class TlsaItem:
    """
    TLSA data needed for one group/service to create
    the corresponding TLSA dns file.

    tlsa_generate_file requires this as input
    Maintain type annotations and avoid cyclic imports
    """
    def __init__(self):

        self.group_name: str = ''
        self.svc_name: str = ''
        self.apex_domain: str = ''
        self.dane_tls: list[DaneTls] = []
        self.db: SslDb
        self.cert: dict[str, SslCert] = {}
        self.ssl_dns: SslDns
        self.lname: str
