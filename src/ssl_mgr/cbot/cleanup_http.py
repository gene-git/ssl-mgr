# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
certbot cleanup hook
 - http push to web server
 - dns - accumulate till have domains for this cert
"""
import os

from utils import open_file
from utils import run_prog

from .auth_push_http import acme_http_token_path
from .certbothook_data import CertbotHookData


def _unlink_file(path: str):
    """ remove file - no errors if not exist """
    if os.path.exists(path):
        try:
            os.unlink(path)
        except OSError:
            pass


def _remove_web_server_token(certbot: CertbotHookData, token_path: str):
    """
    Remove 1 token
    """
    if not (certbot.opts.web and certbot.opts.web.servers):
        return

    for web_serv in certbot.opts.web.servers:
        if web_serv in (certbot.this_host, certbot.this_fqdn):
            rm_cmd = '/usr/bin/rm -f {token_path}'
            pargs = ['/usr/bin/ssh', web_serv, rm_cmd]
            test = certbot.opts.debug
            (_ret, _out, _err) = run_prog(pargs, test=test, verb=True)
        else:
            _unlink_file(token_path)


def cleanup_hook_http(certbot: CertbotHookData):
    """
    clean http-01
       - remove the acme challenge token fils from web server(s)
    """
    # domain = certbot.env.domain
    cb_dir = certbot.db.cb_dir
    web_token_path = acme_http_token_path(cb_dir)

    #
    # List of tokens to be removed from web server(s)
    #
    web_token_data = None
    fobj = open_file(web_token_path, 'r')
    if fobj:
        web_token_data = fobj.read()
        web_token_data = web_token_data.splitlines()
        fobj.close()
    else:
        return

    for token_path in web_token_data:
        _remove_web_server_token(certbot, token_path)

    #
    # Empty tokens from web_token_path so ready
    # for next bunch to be appended
    #
    fobj = open_file(web_token_path, 'w')
    if fobj:
        fobj.close()
