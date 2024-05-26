# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Restart servers after cert update
"""
from typing import List, Union

from utils import run_prog
from ssl_dns import dns_restart

def _check_svc_deps(group_change, services):
    """
    Check if changed domain/service in svc_depends list
    """
    if group_change and group_change.svc_names:
        svc_changed = group_change.svc_names
        found = [svc for svc in svc_changed if svc in services]
        if found:
            return (True, found)
    return (False, None)

def check_depends(changes, server, log) -> bool:
    """
    Check if service changed thats listed as a svc_dep
    """
    if server.svc_depends:
        for svc_dep in server.svc_depends:
            domain = svc_dep.domain
            services = svc_dep.services

            found_change = False
            if domain.lower() in ('*', 'all', 'any'):
                # match any domain
                for (group_name, group_change) in changes.group.items():
                    (got_change, got_svc) = _check_svc_deps(group_change, services)
                    if got_change:
                        found_change = True
                        log(f'   Changed svc_dep: {domain} => {group_name} {got_svc}')
            else:
                # match specific domain
                group_change = changes.group.get(domain)
                (got_change, got_svc) = _check_svc_deps(group_change, services)
                if got_change:
                    found_change = True
                    log(f'   Changed svc_dep: {domain} => {got_svc}')

                #if group_change and group_change.svc_names:
                #    svc_changed = group_change.svc_names
                #    found = [svc for svc in svc_changed if svc in services]
                #    if found:
                #        log(f'svc_depends triggered {found}')
                #        return True
        if found_change:
            return True

    if server.depends and changes.any.depends:
        server_depends_set = set(server.depends)
        found = server_depends_set.intersection(changes.any.depends)
        if found :
            log(f'   depends triggered {found}')
            return True
    return False

def _check_restart_needed(ssl_mgr:'SslMgr', server) -> bool:
    """
    Check if restart needed
    Return True if needed, otherwise False
    """
    logs = ssl_mgr.logs

    if not server or server.restart_cmd :
        return False

    #
    # Check depends and svc_depends
    #
    changes = ssl_mgr.changes
    has_dep_changes = check_depends(changes, server, logs)
    if not has_dep_changes:
        return False

    #
    # restart needed - Check we have privs to do this
    #
    if not ssl_mgr.opts.root_privs:
        logs('  Need root privs to restart server')
        if  ssl_mgr.opts.debug:
            return True
        return False
    return True

def _do_one_restart(ssl_mgr:'SslMgr', cmds:Union[str, List[str]], host=None) -> int:
    """
    Runs command in cmds (or each command if a list)
        - cmds can be single command or list of commands
    return: 
        - the number of fails. 
    For a list of commands each failing command adds to the count
    """
    logs = ssl_mgr.logs
    if not isinstance(cmds, list):
        cmds = [cmds]

    num_fails = 0
    for restart_cmd in cmds:
        this_cmd = restart_cmd.split()
        if not restart_cmd:
            continue

        pargs = []
        if host :
            pargs = ['/usr/bin/ssh', host]

        pargs += this_cmd
        if ssl_mgr.opts.debug:
            logs(f'  debug: {pargs}')
        else:
            [retc, _sout, _serr] = run_prog(pargs, log=ssl_mgr.log)
            if retc != 0:
                logs(f'Error: restarting {pargs}')
                num_fails += 1

    return num_fails

def _restart_server(ssl_mgr:'SslMgr', server) -> (bool, int, int):
    """
    Run restart command on host (local or remote)
    Return (num_fails, num_total)
    The restart command can be 1 item or a list of items to run.
    """
    logs = ssl_mgr.logs
    log = ssl_mgr.log

    restart_needed = _check_restart_needed(ssl_mgr, server)
    if not restart_needed:
        return (True, 0, 0)

    if not server.restart_cmd:
        return (True, 0, 0)

    #
    # NB if restart has more than 1 command, a failure of any of themn counts as a fail.
    #
    num_fails_tot = 0
    num_restarts_tot = 0
    okay = True
    for host in server.servers:
        logs(f'    {host}')
        num_restarts_tot += 1

        #
        # Use ssh if remote otherwise run cmd locally
        #
        remote = None
        if host not in (ssl_mgr.this_host, ssl_mgr.this_fqdn):
            remote = host

        num_fails = _do_one_restart(ssl_mgr, server.restart_cmd, host=remote)

        if num_fails > 0:
            okay = False
            num_fails_tot += 1
            log(f'     Restart : {server.restart_cmd} had {num_fails} fails')

    return (okay, num_fails_tot, num_restarts_tot)

def server_restarts_non_dns(ssl_mgr:'SslMgr') -> bool:
    """
    Restart any non-DNS servers requested in ssl-mgr.conf
     If one server fails to be restarted we continue
    """
    logs = ssl_mgr.logs
    okay = True
    num_fails = 0
    total = 0
    server_types = ('smtp', 'imap', 'web', 'other')
    for stype in server_types:
        server = getattr(ssl_mgr.opts, stype)
        if not server:
            continue
        logs(f'  {stype}: ' )
        (isokay, fails, tots) = _restart_server(ssl_mgr, server)
        num_fails += fails
        total += tots
        if not isokay:
            okay = False

    if not okay or num_fails > 0:
        logs(f'   Error Server restarts : {num_fails} out of {total} failed')

    return okay

def server_restarts_dns(ssl_mgr:'SslMgr') -> bool:
    """
    Restart DNS servers 
    """
    opts = ssl_mgr.opts
    okay = True
    logs = ssl_mgr.logs
    log = ssl_mgr.log
    dns = getattr(ssl_mgr.opts, 'dns')

    restart_needed = _check_restart_needed(ssl_mgr, dns)
    if restart_needed:
        domains = ssl_mgr.changes.dns_domains_changed
        logs(f'  DNS restart for {domains}')
        okay = dns_restart(domains, opts, debug=opts.debug, log=log)
        if not okay:
            logs('   Error DNS restart failed')
    return okay

def server_restarts(ssl_mgr:'SslMgr') -> bool:
    """
    Restart servers
    N.B.
     Order is important, first restart any non-DNS servers (mail etc) 
     so that postfix etc  pick up new certs after a roll
     Must be before dns restart - as once dns is restarted after roll
     only the new cert is advertised - whereas during the roll 
     both curr + next are available via dns.
     So do dns last always.
    """
    logs = ssl_mgr.logs

    logs(' Check non-DNS server reload/restarts')
    if not server_restarts_non_dns(ssl_mgr) :
        return False

    logs(' Checking DNS server reload/restart')
    if not server_restarts_dns(ssl_mgr) :
        return False
    return True
