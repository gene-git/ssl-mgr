# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certificate Tools
"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from config import SslOpts

from .service_conf_check import check_svc
from .service_conf_read import read_svc
from .service_conf_data import ServiceConfData


class ServiceConf(ServiceConfData):
    """
    Descibes one ssl service
     - Includes x509 Name
     - which CA to use
     - key crypto options
     N.B. first san_name must be the primary domain for non-CA certs
    """
    def __init__(self,
                 opts: SslOpts,
                 grp_name: str,
                 svc_name: str):
        """
        Ssl serbive
        """
        super().__init__(opts, grp_name, svc_name)

        if not read_svc(self, opts.top_dir, grp_name, svc_name):
            self.okay = False
            return

        if not check_svc(self):
            self.okay = False
            return

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None
