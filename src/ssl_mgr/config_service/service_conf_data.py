# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Certificate Tools
"""
# pylint: disable=invalid-name, too-many-instance-attributes
# pylint: disable=too-few-public-methods
from config import SslOpts

from .dane_tls import DaneTls


class ServiceConfData:
    """
    Descibes one ssl service
     - Includes x509 Name
     - which CA to use
     - key crypto options
     N.B. first san_name must be the primary domain for non-CA certs
     This is the data, for example, from:
     conf.d/exmaple.com/mail-ec
     Service name : mail-rc
     File contains :
        name, group name, service name
        signing certificate authority
        renew expire days
        dane_tls list of items
        KeyOpts data: (key type, algorirthn)
        X509 data: usual CN, O, OU, L, ST C, email and list of sans
    """
    def __init__(self,
                 opts: SslOpts,
                 grp_name: str,
                 svc_name: str) -> None:
        """
        ServiceConf data base class
        """
        self.name: str = ''
        self.opts: SslOpts = opts
        self.group: str = grp_name  # for non-ca this is also apex_domain
        self.service: str = svc_name
        self.file: str = ''

        self.signing_ca: str = ''
        self.dane_tls: list[DaneTls] = []

        self.debug: bool = False
        self.okay: bool = True

        self.x509 = self.X509()
        self.keyopts = self.KeyOpts()
        self.ca = self.CA()

        self.ftime_ns: int = 0

        #
        # renew when expiry < renew_expire_days
        #  - default inherited from global opts can be changed per svc
        # Do we actually need this - just use opts.xxx
        # self.renew_expire_days = opts.renew_expire_days
        # self.renew_expire_days_spread = opts.renew_expire_days_spread
        # self.renew_info: RenewInfo = opts.renew_info

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None

    class KeyOpts:
        """ Key choice """
        def __init__(self):
            # Default key types
            self.ktype: str = 'ec'
            self.ec_algo: str = 'secp384r1'
            self.rsa_bits: int = 4096

    class X509:
        """ X609 Name  part """
        def __init__(self):
            # X509name
            self.CN = ''
            self.O = ''     # noqa: E741
            self.OU = ''
            self.L = ''
            self.ST = ''
            self.C = ''
            self.email = ''
            self.sans: list[str] = []
            self.group: str = ''
            self.service: str = ''
            # self.file: str = ''

    class CA:
        """ CA info """
        def __init__(self):
            # self.is_ca = False
            # self.is_root = False
            # self.issuer = None
            self.sign_end_days: int = -1
            self.digest: str = ''
