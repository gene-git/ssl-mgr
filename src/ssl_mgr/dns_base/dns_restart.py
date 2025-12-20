# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
DNS support tools
"""

from config import SslOpts
from utils import run_prog
from utils import (Log)


def dns_restart(domains: list[str],
                opts: SslOpts,
                debug: bool = False
                ) -> bool:
    """
    Bump serials, sign zones and restart dns server
    Inputs:
     * dns_restart_cmd script
     * domains
       domain or list of domains to resign,
       if no domain, then restart tool does all
     * opts
       - debug
       - dns_restart_cmd
         takes --serial_bump [domains] as argument

     - Used by dns based auth-hook to update acme-challenge
       RRs for each apex_domain
     - Used by application to update TLSA RRs refresh
       (sign and restart primary)
    """
    logger = Log()
    logsv = logger.logsv
    #
    # Check have permission:
    #
    if not opts.root_privs:
        logsv('   Need root privs to restart dns server')
        if opts.debug:
            return True
        return False

    if not opts.dns:
        logsv(' restart dns: missing opts.dns - fatal')
        return False

    #
    # save DNS RR file
    #
    domains_list: list[str] = []
    if domains:
        if isinstance(domains, str):
            domains_list = [domains]
        else:
            domains_list = domains

    all_ok = True
    for restart_cmd in opts.dns.restart_cmd:
        okay = _dns_restart_one(restart_cmd, domains_list, debug)
        if not okay:
            all_ok = False

    return all_ok


def _dns_restart_one(restart_cmd: str,
                     domains: list[str],
                     debug: bool = False,
                     ) -> bool:
    """
    Bump serials, sign zones and restart dns server
    Inputs:
     * dns_restart_cmd script
     * domains
       domain or list of domains to resign,
       if no domain, then restart tool does all
     - Used by dns based auth-hook to update acme-challenge
       RRs for each apex_domain
     - Used by application to update TLSA RRs refresh
       (sign and restart primary)
    """
    logger = Log()
    logsv = logger.logsv
    #
    # save DNS RR file
    #
    pargs: list[str] = [restart_cmd, '--serial_bump']
    if domains:
        pargs += domains

    if debug:
        logsv(f'  debug dns_restart : {pargs}')
    else:
        (ret, sout, serr) = run_prog(pargs, test=debug, verb=True)
        if sout:
            logsv(sout)
        if ret != 0:
            if serr:
                logsv(serr)
            return False
    return True
