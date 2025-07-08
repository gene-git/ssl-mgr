#!/usr/bin/python
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Crypto primative - certs
Called from ssl_ca.sign_cert()
"""
# pylint: disable=too-many-locals
import os

from crypto_csr import SslCsr
from ca_sign import CACertbot
from utils import Log

from .certbothook import CertbotHook
from .sign_cert import certbot_sign_cert
from .cleanup_http import cleanup_hook_http
from .cleanup_dns import cleanup_hook_dns


def _cleanup_auth(certbot: CertbotHook, ca_certbot: CACertbot):
    """
    Always clean up here as dont use certbot manual-cleanup-hook
     - its easier and 'cleaner' and its possible certbot calls
       clean hook once per (sub)domain. We clean everything in
       one shot. Here:
        - cb_dir/xxx
        - http: web server acme-challenge token files
        - dns: file with TXT records of acme-challenges
    """
    logger = Log()
    logsv = logger.logs
    if ca_certbot.ca_info.ca_validation.startswith('dns'):
        logsv('    Certbot clean up dns')
        cleanup_hook_dns(certbot)
    else:
        logsv('    Certbot clean up http')
        cleanup_hook_http(certbot)


def sign_cert_wrap(ca_certbot: CACertbot, db_dir: str, ssl_csr: SslCsr):
    """
    Give csr to appropriate CA to get a signed cert
    """
    #
    # Signed by letencrypt (via Certbot)
    #
    logger = Log()
    logs = logger.logs

    apex_domain = ssl_csr.svc.group
    service = ssl_csr.svc.service
    opts = ca_certbot.opts

    certbot = CertbotHook('next', apex_domain, service, opts,
                          debug=ca_certbot.debug)

    # maybe excessive check
    db_dir_check = os.path.join(certbot.db.db_dir, certbot.db.db_names['next'])
    if db_dir != db_dir_check:
        txt = f'{db_dir} vs {certbot.db.db_dir}'
        logs(f'Error db_dir != certbot.db.db_dir: {txt}')

    # (cert_pem, chain_pem) = certbot.sign_cert(db_dir, ca_certbot, ssl_csr)
    (cert_pem, chain_pem) = certbot_sign_cert(certbot, ca_certbot, ssl_csr)
    _cleanup_auth(certbot, ca_certbot)

    return (cert_pem, chain_pem)
