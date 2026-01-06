# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
  CA class
"""
# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from ssl_mgr.config import (SslOpts, CAInfo)

from .ca_base import (CaSignType, CABase)


class CACertbot(CABase):
    """
    Letsencrypt Certificate authority used to sign certs.
    via certbot calls.
    - services (domains/item)
    - signed by letsencrypt

    At moment CACertbot is identical to CABase
    """
    def __init__(self, ca_info: CAInfo, opts: SslOpts):
        ca_sign_type = CaSignType.CERTBOT
        super().__init__(ca_sign_type, ca_info, opts)
