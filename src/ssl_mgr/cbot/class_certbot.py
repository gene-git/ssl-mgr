# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
load certbot config
"""
# pylint: disable=invalid-name,too-many-instance-attributes,too-few-public-methods
import os
from db import SslDb
from utils import get_my_hostname
from utils import init_logging, get_certbot_logger
from utils import set_restictive_file_perms
from config import SslOpts
from .auth_hook import auth_hook
from .cleanup_hook import cleanup_hook
from .sign_cert import certbot_sign_cert
from .cleanup_http import cleanup_hook_http
from .cleanup_dns import cleanup_hook_dns

class CertbotHook:
    """
    Used by certbot hook which has less info than when loaded by ssl-mgr
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self, lname:str, grp_name:str, svc_name:str,
                 opts:'SslOpts'=None, debug:bool=False):

        self.lname = lname                  # curr or next
        self.db_name = None
        self.apex_domain = grp_name
        self.svc_name = svc_name
        self.opts = opts

        self.challenge_proto = None         # http or dns

        self.debug = debug

        self.this_host = None
        self.uid = os.geteuid()

        called_from_certbot = False
        if not self.opts:
            called_from_certbot = True
            self.opts = SslOpts(cmdline=False)

        self.logger = get_certbot_logger()
        if not self.logger:
            # running as hook program
            init_logging(self.opts.logdir)
            self.logger = get_certbot_logger()
            self.logger.logs('auth_hook: init logging')

        #
        # certbot logdir (--logs-dir) (default /var/log/letsencrypt)
        #
        self.logdir_letsencrypt = os.path.join(self.opts.logdir, 'letsencrypt')
        os.makedirs(self.logdir_letsencrypt, exist_ok=True)
        set_restictive_file_perms(self.logdir_letsencrypt)

        self.logs = self.logger.logs
        self.logsv = self.logger.logsv
        self.log = self.logger.log
        self.logv = self.logger.logv

        self.log(f'Cerbothook: {grp_name} {svc_name} ')

        self.db = SslDb(self.opts.top_dir, grp_name, svc_name)
        self.cb_dir = self.db.cb_dir
        self.db_name = self.db.db_names[lname]

        #
        # certbot work dir (--work-dir)(default is /var/lib/letsencrypt)
        #
        self.workdir_letsencrypt = os.path.join(self.cb_dir, 'work')
        set_restictive_file_perms(self.workdir_letsencrypt)

        (self.this_host, self.this_fqdn) = get_my_hostname()

        self.env = self.Env(self.log)
        if called_from_certbot:
            # no point unless certbot manual auth hook
            self.env.refresh()

    class Env:
        """ certbot hooks get env variables """
        def __init__(self, log):
            #
            # for auth and cleanup
            #
            self.domain = None
            self.validation = None
            self.token = None
            self.remaining_challenges = 0
            self.all_domains = []
            self.log = log
            #
            # for cleanup
            #
            self.auth_output = None

        def refresh(self):
            """
            Fetch certbot env variables
            """
            # for auth and cleanup
            self.domain = os.getenv('CERTBOT_DOMAIN')
            self.validation = os.getenv('CERTBOT_VALIDATION')
            self.token = os.getenv('CERTBOT_TOKEN')
            self.remaining_challenges = os.getenv('CERTBOT_REMAINING_CHALLENGES')
            if self.remaining_challenges:
                self.remaining_challenges = int(self.remaining_challenges)
            else:
                self.remaining_challenges=0
            self.all_domains = os.getenv('CERTBOT_ALL_DOMAINS')
            if self.all_domains:
                self.all_domains = self.all_domains.split(',')

            # for cleanup
            self.auth_output = os.getenv('CERTBOT_AUTH_OUTPUT')

            # self.log(f'cerbothook Env: domain={self.domain}')

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

def _cleanup_auth(certbot, ssl_ca):
    """
    Always clean up here as dont use certbot manual-cleanup-hook
     - its easier and 'cleaner' and its possible certbot calls
       clean hook once per (sub)domain. We clean everything in
       one shot. Here:
        - cb_dir/xxx
        - http: web server acme-challenge token files
        - dns: file with TXT records of acme-challenges
    """
    logsv = certbot.logs
    if ssl_ca.info.ca_validation.startswith('dns'):
        logsv('Certbot clean up dns')
        cleanup_hook_dns(certbot)
    else:
        logsv('Certbot clean up http')
        cleanup_hook_http(certbot)

class Certbot(CertbotHook):
    """
    Used by ssl-mgr
    """
    #def __init__(self, link_name:str, grp_name:str, svc_name:str, opts:'SslOpts'):
    #    super().__init__(link_name:str, grp_name:str, svc_name:str)
    #    self.opts = opts

    def sign_cert(self, db_dir:str, ssl_ca:'SslCA', ssl_csr:'SslCsr'):
        """
        request new cert for this grp_name:svc_name
         - Sends email etc to allow letsencrypt account registration
         - db_dir should be same as certbot.db.db_dir/db/<next>
        """
        db_dir_check = os.path.join(self.db.db_dir, self.db.db_names['next'])
        if db_dir != db_dir_check:
            self.logs(f'Error db_dir != self.db.db_dir: {db_dir} vs {self.db.db_dir}')

        (cert_pem, chain_pem) = certbot_sign_cert(self, ssl_ca, ssl_csr)
        _cleanup_auth(self, ssl_ca)

        return (cert_pem, chain_pem)
