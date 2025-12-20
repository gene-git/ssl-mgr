# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
load certbot config
"""
# pylint: disable=invalid-name, too-many-instance-attributes
# pylint: disable=too-few-public-methods
import os

from db import SslDb
from utils import get_my_hostname
from utils import (Log, LogZone)
from utils import set_restictive_file_perms
from config import SslOpts


class CertbotHookData:
    """
    Base class with data (no methods)
    Used by certbot hook. CertbotHook is passed in and called via certbot
    external executable (as a "hook").
    This uses less info/data than Certbot which
    is called from from sslm-mgr itself.
    """
    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(self,
                 lname: str,
                 grp_name: str,
                 svc_name: str,
                 opts: SslOpts,  # | None = None,
                 debug: bool = False):

        self.lname: str = lname                  # curr or next
        self.db_name: str = ''
        self.apex_domain: str = grp_name
        self.svc_name: str = svc_name
        self.opts: SslOpts = opts

        self.challenge_proto: str = ''         # http or dns

        self.debug: bool = debug

        self.this_host: str = ''
        self.uid: int = os.geteuid()

        #
        # called_from_certbot via cerbot ->sslm-auth-hook
        # old was cmdline = false means called from certbot
        #
        called_from_certbot: bool = opts.called_from_certbot

        logger = Log()
        if not logger.is_initialized():
            # running as hook program
            logger.initialize(self.opts.logdir, zone=LogZone.CERTBOT)
            logger.logs('auth_hook: init logging')

        #
        # certbot logdir (--logs-dir) (default /var/log/letsencrypt)
        #
        self.logdir_letsencrypt = os.path.join(self.opts.logdir, 'letsencrypt')
        os.makedirs(self.logdir_letsencrypt, exist_ok=True)
        set_restictive_file_perms(self.logdir_letsencrypt)

        logger.log(f'Cerbothook: {grp_name} {svc_name} ')

        self.db = SslDb(self.opts.top_dir, grp_name, svc_name)
        self.cb_dir = self.db.cb_dir
        self.db_name = self.db.db_names[lname]

        #
        # certbot work dir (--work-dir)(default is /var/lib/letsencrypt)
        #
        self.workdir_letsencrypt = os.path.join(self.cb_dir, 'work')
        set_restictive_file_perms(self.workdir_letsencrypt)

        (self.this_host, self.this_fqdn) = get_my_hostname()

        self.env = self.Env()
        if called_from_certbot:
            # no point unless certbot manual auth hook
            self.env.refresh()

    class Env:
        """ certbot hooks get env variables """
        def __init__(self):
            #
            # for auth and cleanup
            #
            self.domain: str = ''
            self.validation: str = ''
            self.token: str = ''
            self.remaining_challenges: int = 0
            self.all_domains: list[str] = []
            #
            # for cleanup
            #
            self.auth_output: str = ''

        def refresh(self):
            """
            Fetch certbot env variables
            """
            # for auth and cleanup
            self.domain = ''
            domain = os.getenv('CERTBOT_DOMAIN')
            if domain:
                self.domain = domain

            self.validation = ''
            validation = os.getenv('CERTBOT_VALIDATION')
            if validation:
                self.validation = validation

            self.token = ''
            token = os.getenv('CERTBOT_TOKEN')
            if token:
                self.token = token

            remaining_challenges = os.getenv('CERTBOT_REMAINING_CHALLENGES')
            if remaining_challenges:
                self.remaining_challenges = int(remaining_challenges)
            else:
                self.remaining_challenges = 0

            all_domains = os.getenv('CERTBOT_ALL_DOMAINS')
            if all_domains:
                self.all_domains = all_domains.split(',')
            else:
                self.all_domains = []

            # for cleanup
            auth_output = os.getenv('CERTBOT_AUTH_OUTPUT')
            if not auth_output:
                auth_output = ''

            # logger.log(f'cerbothook Env: domain={self.domain}')
