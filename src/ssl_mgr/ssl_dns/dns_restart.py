# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
DNS support tools
"""
# pylint: disable=duplicate-code
from utils import run_prog

def dns_restart(domains, opts:'SslOpts', debug:bool=False, log=print):
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

     - Used by dns based auth-hook to update acme-challenge RRs for each apex_domain
     - Used by application to update TLSA RRs refresh (sign and restart primary)
       
    """
    #
    # Check have permission:
    #
    if not opts.root_privs :
        log('   Need root privs to restart dns server')
        if opts.debug:
            return True
        return False

    #
    # save DNS RR file
    #
    dns_restart_cmd = opts.dns.restart_cmd
    pargs = [dns_restart_cmd, '--serial_bump']
    if domains:
        if isinstance(domains, str):
            pargs += [domains]
        else:
            pargs += domains

    if debug:
        log(f'  debug dns_restart : {pargs}')
    else:
        [ret, sout, serr] = run_prog(pargs, log=log)
        if sout:
            log(sout)
        if ret != 0 :
            if serr:
                log(serr)
            return False
    return True
