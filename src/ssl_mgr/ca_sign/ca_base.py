# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
  CA class
"""
# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from ssl_mgr.config import (SslOpts, CAInfo)
from ssl_mgr.config_service import (ServiceConf)

from .ca_types import CaSignType


class CABase():
    """
    Base class for certificate authority which
    signs/issues certs.

    See CASelf and CACertbot classes.
    Signing CAs used by:
     - clients (domains)
       - signed by local intermediate (sub) CA
       - signed by letsencrypt
     - local sub CA itself gets signed by local root CA
    """
    def __init__(self,
                 ca_sign_type: CaSignType,
                 ca_info: CAInfo,
                 opts: SslOpts):

        self.okay: bool = True
        self.group: str = 'ca'
        self.service: str = ''
        self.ca_info: CAInfo = ca_info
        self.svc: ServiceConf
        self.opts: SslOpts = opts
        self.ca_sign_type: CaSignType = ca_sign_type
        # self.cert: CertData | None = None

        #
        # Options to pass to CA
        #
        self.test: bool = False
        self.dry_run: bool = False
        self.debug: bool = False
