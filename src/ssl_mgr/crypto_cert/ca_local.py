# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  CA class
"""
# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from db import SslDb
from config import (SslOpts, CAInfo)
from config_service import ServiceConf
from ca_sign import (CABase, CaSignType)
from utils import Log

from ._cert_data import CertData


class CALocal(CABase):
    """
    Certificate to be signed by
    local certificate Authority which is signed by
    local (self signed) root cert.
    - services (domains/item)
    - signed by local intermediate (sub) CA
    - local sub CA itself is signed by local root CA
    """
    def __init__(self, ca_info: CAInfo, opts: SslOpts):

        self.cert: CertData

        ca_sign_type = CaSignType.LOCAL
        super().__init__(ca_sign_type, ca_info, opts)

        #
        # Since CA is local, read the CA svc config
        #
        ca_name = ca_info.ca_name
        self.svc = ServiceConf(opts, self.group, ca_name)
        self.db = SslDb(opts.top_dir, self.group, ca_name)
        db_name = self.db.db_names['curr']
        logger = Log()
        if not db_name:
            logger.logs('Error: CASelf has no current cert/keys')
            self.okay = False
            return

        self.cert = CertData(db_name, self.svc, self.db,
                             self.group, ca_name, opts)
