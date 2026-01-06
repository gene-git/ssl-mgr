# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
# pylint: disable=too-many-locals
"""
certbot auth hook
 - cerbot runs standaline program
   sslm_auth_hook='/usr/lib/ssl-mgr/sslm-auth-hook
 - this supports that executable
 - http push to web server
 - dns has file with acme-challenges copied to dns zone include area
   then zone(s) are signed and pushed to dns-primary server
 - certbot calls this hook for each domain in cert.
   We accumulate till have all domains for this cert.
   certbot sets env variables
   e.g. telling us when last (sub) domain is passed in which we then
   use to trigger sending all acme-challenges out
   (to web or dns server as appropriate)
"""
import os
# from .class_certbot import Certbot
from ssl_mgr.utils import open_file
from ssl_mgr.utils import read_file
from ssl_mgr.utils import rename_backup
from ssl_mgr.utils import Log

from .certbothook_data import CertbotHookData
from .auth_push import auth_push


def auth_hook(certbot: CertbotHookData):
    """
    Auth hook handler
    """
    logger = Log()
    log = logger.log

    result = ''
    certbot.env.refresh()
    domain = certbot.env.domain
    validation = certbot.env.validation
    token = certbot.env.token
    remaining_challenges = certbot.env.remaining_challenges
    #
    # Update log file
    #
    log(f'auth_hook: domain = {domain}')
    log(f'auth_hook: validation = {validation}')
    log(f'auth_hook: token = {token}')
    log(f'auth_hook: remaining_challenges = {remaining_challenges}')

    #
    # token being set is a good way to determine http vs dns
    # As certbot only sends token for http
    # Should match ssl_ca.info.ca_validation (our request to certbot)
    #
    if token:
        certbot.challenge_proto = 'http'
    else:
        certbot.challenge_proto = 'dns'

    log(f'auth_hook: challenge_proto = {certbot.challenge_proto}')

    #
    # Keep all data in file until all domains have been processed
    #  - We pass down group-service to hook - use to keep
    #    our data has domain as apex dir
    #
    cb_dir = certbot.db.cb_dir
    auth_data_file = 'auth-data'
    auth_data_path = os.path.join(cb_dir, auth_data_file)

    if token:
        # http challenge
        data = f'{domain} {validation} {token}\n'
    else:
        # dns challenge
        data = f'{domain} {validation}\n'

    if os.path.exists(auth_data_path):
        # subsequent calls for this cert => Append each (sub)domain
        fobj = open_file(auth_data_path, 'a')
        if not fobj:
            log(f'Fatal error opening file {auth_data_path}')
            raise OSError(f'Fatal error opening file {auth_data_path}')
    else:
        # first call for this cert => create new auth_data file
        fobj = open_file(auth_data_path, 'w')
        if not fobj:
            log(f'Fatal error opening file {auth_data_path}')
            raise OSError(f'Fatal error opening file {auth_data_path}')
        hdr = f'# {domain} {certbot.challenge_proto}\n'
        hdr += f'# Domains = {certbot.env.all_domains}\n'
        fobj.write(hdr)

    # Save this (sub)domain's challenge into auth_data
    fobj.write(data)
    fobj.close()

    # When all done => push them out
    if remaining_challenges == 0:
        log('auth_hook: last challenge => auth_push')

        #
        # Read back all the challenges
        #
        auth_data = read_file(cb_dir, auth_data_file)

        #
        # rename auth_data file so is not reused
        # (could also remove os.unlink(auth_data_path))
        #
        rename_backup(auth_data_path, ".prev")

        #
        # Push all challenges out
        #
        if auth_data:
            auth_data_rows = auth_data.splitlines()
            auth_push(certbot, auth_data_rows)
        else:
            log(f'empty auth data - wow, not possible! {auth_data_path}')

    return result
