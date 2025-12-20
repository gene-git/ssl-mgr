# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
certbot cleanup hook
 - http push to web server
 - dns - accumulate till have domains for this cert
"""
from .auth_push_dns import auth_push_dns
from .certbothook_data import CertbotHookData


def cleanup_hook_dns(certbot: CertbotHookData):
    """
    clean dns-01
     - make new/empty file - i.e. no TXT records with challenge tokens.
     - push to DNS
     - be nice if could hold the actual push until we are ready
       to push dns for tlsa (even if no tlsa)
       Dont have svc so no sans - its in csr
    """
    apex_domain = certbot.apex_domain
    svc_name = certbot.svc_name         # or certbot.db.service
    cb_dir = certbot.cb_dir

    auth_data_rows = []
    auth_data_rows.append(f';; dns : {apex_domain} {svc_name}')
    auth_data_rows.append(f';; cb  : {cb_dir}')
    auth_data_rows.append(';; Done - cleaned up')

    #
    # Push empty acme-challenge dns zone file
    # (skip waiting for nameserver checks
    # as we are not validating any acme challenges)
    # Maybe we can delay this push until tlsa records are available?
    #
    auth_push_dns(certbot, auth_data_rows, check_nameservers=False)
