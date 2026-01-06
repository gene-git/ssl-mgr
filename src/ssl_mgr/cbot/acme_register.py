# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
(Re)New cert from letsencrypt
"""
# pylint: disable=too-many-locals
import time

from pyconcurrent import run_prog

from ssl_mgr.utils import Log
from ssl_mgr.crypto_csr import SslCsr
from ssl_mgr.ca_sign import CACertbot

from .certbothook_data import CertbotHookData
from .acct_registered import acct_registered


def _certbot_register_options(certbot: CertbotHookData, ssl_csr: SslCsr
                              ) -> list[str]:
    """
    Construct options to pass to certbot
     - Cerbot puts account info into 'config-dir'
    """
    #
    # cb_dir is for certbot to keep account info etc.
    #
    cb_dir = certbot.db.cb_dir
    email = ssl_csr.svc.x509.email

    opts = ['register']
    # opts += ['--quiet']
    opts += ['--config-dir', cb_dir]
    opts += ['--logs-dir', certbot.logdir_letsencrypt]
    opts += ['--work-dir', certbot.workdir_letsencrypt]
    opts += ['--agree-tos', '--no-eff-email', '--email', email]

    if certbot.opts.test:
        opts += ['--test-cert']

    if certbot.opts.dry_run:
        opts += ['--dry-run']

    return opts


def certbot_acct_check(certbot: CertbotHookData, ca_certbot: CACertbot,
                       ssl_csr: SslCsr) -> bool:
    """
    Check if acme account registered, if not register letsencrypt ACME account
     - This must be done before attmpeting to get a certificate
       in manual mode certbot only works with account already registered.
    returns True if account already registered or success registering now.
            False if failed to register new account
    """
    logger = Log()
    logs = logger.logs
    log = logger.log

    cb_dir = certbot.db.cb_dir
    apex_domain = certbot.apex_domain
    service = ssl_csr.svc.service

    #
    # Check if LE account already registered
    # stop using ca_certbot.test - now use command line -t / -n
    #
    is_staging = certbot.opts.test
    acct_is_reg = acct_registered(certbot.db.cb_dir, staging=is_staging)
    if acct_is_reg:
        return True

    logs(f'  Registering ACME acct {apex_domain}/{service} : {cb_dir}')

    #
    # certbot does the work
    #
    reg_opts = _certbot_register_options(certbot, ssl_csr)

    cmd = ['/usr/bin/certbot']
    pargs = cmd + reg_opts

    log(f'Certbot command: {pargs}')
    if not ca_certbot.debug:
        test = certbot.opts.debug
        (ret, _sout, _serr) = run_prog(pargs, test=test, verb=True)
        if ret != 0:
            logs(f'  Error registering account {apex_domain}/{service}')
            return False

        #
        # after new account,  we need to give letsencrypt time before using it
        # Ad hoc timeout
        #
        le_timeout = 2
        txt = f'Ad hoc sleep before using new account: {le_timeout} secs'
        logs(f'  {txt}')
        time.sleep(le_timeout)

    return True
