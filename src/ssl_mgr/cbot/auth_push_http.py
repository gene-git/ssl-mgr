# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Worked functions
"""
from typing import (IO)
import os
import stat
from pwd import getpwnam
from grp import getgrnam
import tempfile

from utils import open_file, run_prog, make_dir_path, write_path_atomic
from utils import Log

from .certbothook_data import CertbotHookData


def _fix_file_permission(certbot: CertbotHookData, token_path: str):
    """
    Token must be readable by webserver
     - we assume uid/gid for user 'http' is same on this machine as on
       web server
    """
    logger = Log()
    logs = logger.logs

    user_http = 'http'
    http_uid = getpwnam(user_http).pw_uid
    http_gid = getgrnam(user_http).gr_gid

    file_mode = stat.S_IRUSR | stat.S_IWUSR
    file_mode |= stat.S_IRGRP | stat.S_IROTH
    try:
        os.chmod(token_path, file_mode)
    except OSError as err:
        logs(f'  Failed to chmod {token_path} : {err}')

    if certbot.uid == 0:
        try:
            os.chown(token_path, http_uid, http_gid)
        except OSError as err:
            txt = f'{http_uid}:{http_gid}: {err}'
            logs(f'  Failed to chown {token_path} to {txt}')
    else:
        logs('  http push needs root to change file owner/group')


def _token_to_webservers(certbot: CertbotHookData,
                         token_path: str,
                         validation: str):
    """
    Copy the acme validation token to one or more web servers
     - <server>/<domain>/.well-known/acme-challenge/<token>
     - if same machine copy (make temp file) otherwise use scp
       (make sure scp has right permissions to work with no passphrase prompt)
    -
      make sure web server can read file.
      Be sure remote web server(s) use same uuid for user http as this machine
       - if not we'll need to fix code to change remote file owner
    """
    # pylint: disable=line-too-long
    logger = Log()

    val_data = validation + '\n'
    temp_token: IO | None = None
    for web_server in certbot.opts.web.servers:
        if web_server in (certbot.this_host, certbot.this_fqdn):
            #
            # remote server
            #
            if not temp_token:
                with tempfile.NamedTemporaryFile(mode='w',
                                                 prefix='cb-',
                                                 delete=False) as temp_token:
                    temp_token.write(val_data)
                _fix_file_permission(certbot, temp_token.name)

            scp = '/usr/bin/scp'

            dst = f'{web_server}:{token_path}'
            pargs = [scp, temp_token.name, dst]
            test = certbot.opts.debug
            (_ret, _sout, _serr) = run_prog(pargs, test=test, verb=True)

        else:
            #
            # Same machine - write file
            #
            write_path_atomic(val_data, token_path, logger.logs)
            _fix_file_permission(certbot, token_path)

    if temp_token:
        os.unlink(temp_token.name)


def acme_http_token_path(cb_dir: str) -> str:
    """
    File used to save list of all the acme
    validation tokens.
    Cleanup uses this to remove each challengre file from web server
    """
    web_token_path = os.path.join(cb_dir, 'web-tokens')
    return web_token_path


def _save_web_tokens(cb_dir: str, web_token_data: str):
    """
    Save token paths for clean_hook to remove
    We assume we get all domains for this cert
    so can use 'w' instead of 'a'
    """
    logger = Log()
    logs = logger.logs

    web_token_path = acme_http_token_path(cb_dir)
    fobj = open_file(web_token_path, 'w')
    if fobj:
        fobj.write(web_token_data)
        fobj.close()
    else:
        logs(f'Failed to save web_tokes to {web_token_path}')


def auth_push_http(certbot: CertbotHookData,
                   auth_data_rows: list[str]):
    """
    Push each validation string to the token file on web server
    each row is: domain validation token
    """
    # pylint: disable=too-many-locals
    logger = Log()
    log = logger.logs
    logs = logger.logs

    logs('auth_push_http', opt='sdash')

    apex_domain = certbot.apex_domain

    acme = '.well-known/acme-challenge'
    web_token_data = ''

    for row in auth_data_rows:
        if row.startswith('#') or row.startswith(';'):
            continue

        (domain, validation, token) = row.split()
        log(f'  {domain} {validation} {token}')

        #
        # x.apex_domain has its web data served from .../apex_domain/...
        #   e.g. /srv/https/Sites/<apex_domain>/.well-known/acme-challenge
        # So we dont actually use 'domain'
        #
        web_dir = os.path.join(certbot.opts.web.server_dir, apex_domain)
        token_path = os.path.join(web_dir, acme, token)

        # Keep the list of token paths so they can be removed in clean up
        web_token_data += token_path + '\n'

        log(f'  {token_path}')
        if certbot.debug:
            test_token_path = os.path.join(certbot.db.cb_dir, 'tokens')
            make_dir_path(test_token_path)
            test_token_path = os.path.join(test_token_path, token)
            logs(f'Deb skip: push webserver : {domain} -> {token_path}')
            logs(f'    copy: {test_token_path}')
            val_data = validation + 'n'
            write_path_atomic(val_data, test_token_path, log=logs)
            continue

        # copy to web server(s)
        _token_to_webservers(certbot, token_path, validation)

    #
    # Save token paths for clean_hook to remove
    # We assume we get all domains for this cert
    # so can use 'w' instead of 'a'
    #
    logs('  saving web-tokens')
    cb_dir = certbot.db.cb_dir
    _save_web_tokens(cb_dir, web_token_data)
