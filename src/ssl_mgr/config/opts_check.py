# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Basic checks on config and options
"""
import os

from utils import Log

from ._opts_data import SslOptsData


def _check_dns(opts: SslOptsData):
    """
    need server/port
    """
    okay = True
    logger = Log()
    logs = logger.logs
    if not opts.dns:
        txt = 'TLSA, acme DNS-01 et al not supported '
        logs(f'Warning: DNS Missing from config: {txt} ')

    return okay


def check_dns_primary(opts: SslOptsData):
    """
    need server/port
    """
    okay = True
    logger = Log()
    logs = logger.logs

    if not opts.dns_primary or not isinstance(opts.dns_primary, list):
        logs('Warning: Missing dns_primary tables in config')
        return True

    for primary in opts.dns_primary:
        domain = primary.get('domain')
        server = primary.get('server')
        port = primary.get('port')
        if not domain or not server or not port:
            txt = f'{domain} {server} {port}'
            logs(f'Error: config dns_primary bad item : {txt}')
            okay = False
    return okay


def _check_post_copy_command(opts: SslOptsData):
    """
    Check copy command syntax
    """
    logger = Log()
    logs = logger.logs

    if not opts.post_copy_cmd:
        return True

    if not isinstance(opts.post_copy_cmd, list):
        logs('Error: post_copy_cmd must be a list')
        return False

    okay = True
    for item in opts.post_copy_cmd:
        if not isinstance(item, list):
            txt = f'[host, cmd] not {item}'
            logs(f'Error: post_copy_cmd element must be {txt}')
            okay = False
            continue
    return okay


def check_cainfo(opts: SslOptsData) -> bool:
    """
    Check at least one CA is in ca-info.conf
    """
    logger = Log()
    logs = logger.logs

    if not opts.ca_infos:
        logs('Error: no certicate authority infos found (ca-info.conf)')
        return False
    return True


def check_options(opts: SslOptsData):
    """
    Check when called by sslm-mgr
    """
    okay = True
    if not _check_dns(opts):
        okay = False

    if not check_cainfo(opts):
        okay = False

    logger = Log()
    logs = logger.logs

    if not opts.prod_cert_dir:
        logs('Error: Missing prod_cert_dir in config')
        okay = False

    if not opts.grps_svcs:
        logs('Warning: No groups/services provided')

    clean_keep_min = 1
    if opts.clean_keep < clean_keep_min:
        txt = f'{opts.clean_keep} resetting to {clean_keep_min}'
        logs(f'Info: clean_keep too small {txt}')
        opts.clean_keep = max(opts.clean_keep, clean_keep_min)

    if not _check_post_copy_command(opts):
        okay = False

    return okay


def check_options_cbot_hook(opts: SslOptsData):
    """
    Check when called by sslm-auth-hook
    """
    okay = True
    if not _check_dns(opts):
        okay = False

    if not check_dns_primary(opts):
        okay = False

    logger = Log()
    logs = logger.logs

    if opts.dns:
        if not opts.dns.acme_dir:
            logs('Warning: Missing dns.acme_dir in config')
    else:
        logs('Warning: Missing opts.dns in config')

    return okay


def check_options_group(group_name: str,
                        services: list[str],
                        opts: SslOptsData) -> bool:
    """
    Confirm group has service configs
    SslMgr() ignores any group with no services.
    """
    logger = Log()
    logs = logger.logs
    okay = True

    group_dir = os.path.join(opts.conf_dir, group_name)
    if not os.path.isdir(group_dir):
        logs(f'Error: No such group - directory missing {group_dir}')
        okay = False

    if not services:
        logs(f'Error: Group {group_name} missing services')
        okay = False

    if not (opts.web and opts.web.server_dir):
        txt = 'missing web.server_dir'
        logs(f'Warning: acme HTTP-01 not available - {txt}')

    if not check_dns_primary(opts):
        txt = 'missing dns primary server / port'
        logs(f'Warning: acme dns not available: {txt}')

    for svc_name in services:
        if svc_name in ('*', 'ALL'):
            continue
        svc_file = os.path.join(group_dir, svc_name)
        if not os.path.exists(svc_file):
            logs(f'Error No config for {group_name}:{svc_name}')
            okay = False
    return okay
