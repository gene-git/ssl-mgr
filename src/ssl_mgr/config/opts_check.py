# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Basic checks on config and options
"""
import os

def _check_dns(log, opts):
    """
    need server/port
    """
    okay = True
    if not opts.dns:
        log('Warning: DNS Missing from config - TLSA, acme DNS-01 et al not supported ')

    return okay

def check_dns_primary(log, opts):
    """
    need server/port
    """
    okay = True

    if not opts.dns_primary or not isinstance(opts.dns_primary, list):
        log('Warning: Missing dns_primary tables in config')
        return True

    for primary in opts.dns_primary:
        domain = primary.get('domain')
        server = primary.get('server')
        port = primary.get('port')
        if not domain or not server or not port:
            log(f'Error: config dns_primary bad item : {domain} {server} {port}')
            okay = False
    return okay

def check_options(log, opts:"SslOpts"):
    """
    Check when called by sslm-mgr
    """
    okay = True
    if not _check_dns(log, opts):
        okay = False

    if not opts.prod_cert_dir:
        log('Error: Missing prod_cert_dir in config')
        okay = False

    if not opts.grps_svcs:
        log('Warning: No groups/services provided')

    clean_keep_min = 1
    if opts.clean_keep < clean_keep_min:
        log(f'Info: clean_keep too small {opts.clean_keep} resetting to {clean_keep_min}')
        opts.clean_keep = max(opts.clean_keep, clean_keep_min)

    return okay

def check_options_cbot_hook(log, opts:"SslOpts"):
    """
    Check when called by sslm-auth-hook
    """
    okay = True
    if not _check_dns(log, opts):
        okay = False

    if not check_dns_primary(log, opts):
        okay = False

    if opts.dns:
        if not opts.dns.acme_dir:
            log('Warning: Missing dns.acme_dir in config')
    else:
        log('Warning: Missing opts.dns in config')
        #okay = False

    return okay

def check_options_group(log, group_name:str, services:[str], opts:"SslOpts") -> bool:
    """
    Confirm group has service configs
    SslMgr() ignores any group with no services.
    """
    okay = True
    group_dir = os.path.join(opts.conf_dir, group_name)
    if not os.path.isdir(group_dir):
        log(f'Error: No such group - directory missing {group_dir}')
        okay = False

    if not services:
        log(f'Error: Group {group_name} missing services')
        okay = False

    if not (opts.web and opts.web.server_dir):
        log('Warning: acme HTTP-01 not available - missing web.server_dir')

    if not check_dns_primary(log, opts):
        log('Warning: acme dns not available - missing dns primary server / port')
        #okay = False

    for svc_name in services:
        svc_file = os.path.join(group_dir, svc_name)
        if not os.path.exists(svc_file):
            log(f'Error No config for {group_name}:{svc_name}')
            okay = False
    return okay
