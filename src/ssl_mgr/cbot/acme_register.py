# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
(Re)New cert from letsencrypt
"""
# pylint: disable=too-many-locals
import time
from utils import run_prog
from .acct_registered import acct_registered

def certbot_register_options(certbot:'Certbot', ssl_csr:'SslCsr'):
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
    #opts += ['--quiet']
    opts += ['--config-dir', cb_dir]
    opts += ['--agree-tos', '--no-eff-email', '--email', email]

    return opts

def certbot_acct_check(certbot:'Certbot', ssl_ca:'SslCA',  ssl_csr:'SslCsr'):
    """
    Check if acme account registered, if not register letsencrypt ACME account
     - This must be done before attmpeting to get a certificate
       in manual mode certbot only works with account already registered.
    returns True if account already registered or success registering now.
            False if failed to register new account
    """
    logs = certbot.logs
    log = certbot.log

    cb_dir = certbot.db.cb_dir
    apex_domain = certbot.apex_domain
    service = ssl_csr.svc.service

    #
    # Check if LE account already registered
    #
    is_staging = ssl_ca.test
    acct_is_reg = acct_registered(certbot.db.cb_dir, staging=is_staging)
    if acct_is_reg:
        return True

    logs(f'  Registering ACME acct {apex_domain}/{service} : {cb_dir}')

    #
    # certbot does the work
    #
    reg_opts = certbot_register_options(certbot, ssl_csr)

    cmd = ['/usr/bin/certbot']
    pargs = cmd + reg_opts

    log(f'Certbot command: {pargs}')
    if not ssl_ca.debug:
        [ret, _sout, _serr] = run_prog(pargs, log=logs)
        if ret != 0:
            logs(f'  Error registering account {apex_domain}/{service}')
            return False

        #
        # after new account,  we need to give letsencrypt time before using it
        # Ad hoc timeout
        #
        le_timeout = 2
        logs(f'  Ad hoc sleep after new account before using it ({le_timeout} secs)')
        time.sleep(le_timeout)

    return True
