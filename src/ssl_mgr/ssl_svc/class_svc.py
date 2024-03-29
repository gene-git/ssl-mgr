# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Certificate Tools
"""
# pylint: disable=invalid-name,too-many-instance-attributes
from utils import get_logger
from .svc_check import check_svc
from .svc_read import read_svc

class SslSvc:
    """
    Descibes one ssl service
     - Includes x509 Name
     - which CA to use
     - key crypto options 
     N.B. first san_name must be the primary domain for non-CA certs
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, opts:'SslOpts', grp_name:str, svc_name:str) -> None:
        self.name = None
        self.opts = opts
        self.group = grp_name          # for non-ca this is also apex_domain
        self.service = svc_name

        self.signing_ca = None
        self.dane_tls = []

        self.debug = False
        self.okay = True

        self.logger = get_logger()
        self.log = self.logger.log
        self.logs = self.logger.logs
        self.logsv = self.logger.logsv

        self.x509 = self.X509()
        self.keyopts = self.KeyOpts()
        self.ca = None

        self.ftime_ns = None

        #
        # renew when expiry < renew_expire_days
        #  - default inherited from global opts can be changed per svc
        #
        self.renew_expire_days = opts.renew_expire_days

        if not read_svc(self, opts.top_dir, grp_name, svc_name, self.logs):
            self.okay = False
            return

        if not check_svc(self, self.logs):
            self.okay = False
            return

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None


    class KeyOpts:
        """ Key choice """
        def __init__(self):
            # Default key types
            self.ktype = 'ec'
            self.ec_algo = 'secp384r1'
            self.rsa_bits = 4096

    class X509:
        """ X609 Name  part """
        def __init__(self):
            # X509name
            self.CN = ''
            self.O = ''
            self.OU = ''
            self.L = ''
            self.ST = ''
            self.C = ''
            self.email = ''
            self.sans = []
            self.group = None
            self.service = None
            self.file = None

    class CA:
        """ CA info """
        def __init__(self):
            #self.is_ca = False
            #self.is_root = False
            #self.issuer = None
            self.sign_end_days = None
            self.digest = None
