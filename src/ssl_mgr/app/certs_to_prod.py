# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Push keys/certs to designated directory
 prod_cert_dir: defined in ssh-mgr.conf
"""
import os
from utils import make_dir_path, run_prog

def _copy_local_prod(ssl_mgr:"SslMgr") -> bool:
    """
    Copy from certs/group/svc -> prod_cert_dir
    """
    prod_cert_dir = ssl_mgr.opts.prod_cert_dir
    if not os.path.exists(prod_cert_dir):
        isok = make_dir_path(prod_cert_dir)
        if not isok:
            ssl_mgr.logs(f'Error - Failed to make dir {prod_cert_dir}')
            return False

    # copy groups 1 at a time
    for (grp_name, group) in ssl_mgr.groups.items():
        ssl_mgr.logsv(f'  -> prod {grp_name}')
        prod_group_dir = os.path.join(prod_cert_dir, grp_name)

        if not group.to_production(prod_group_dir):
            return False
    return True

def _copy_local_to_remote(ssl_mgr, host) -> bool:
    """
    Copy production certs/keys to remote server
     - Skip if host is note remote
    """
    # pylint: disable=duplicate-code
    #
    # Only do remote hosts
    #
    if host in (ssl_mgr.this_host, ssl_mgr.this_fqdn):
        # skip as already copied to myself (local) host
        return True
    logs = ssl_mgr.logs

    #
    # copy contents to same remote dir
    #
    cert_dir = f'{ssl_mgr.opts.prod_cert_dir}/'
    remote_cert_dir = f'{host}:{cert_dir}'

    #
    # Cannot copy remote if cert_dir not absolute path:
    #
    if cert_dir[0] == '.':
        logs(f'  Error: remote copy must be absolute path : {cert_dir}')
        return False

    pargs = ['/usr/bin/rsync', '-a', '--mkpath', cert_dir, remote_cert_dir]
    if ssl_mgr.opts.debug:
        logs(f'  debug: {pargs}')
    else:
        logs(f'  Copying certs to remote {host}')
        [retc, _sout, _serr] = run_prog(pargs, log=ssl_mgr.log)
        if retc != 0:
            logs(f'Error: copying certs to {remote_cert_dir}')
            return False
    return True

def _copy_to_server(ssl_mgr, serv_class, servers_done, log):
    """
    Copy production cers to server
    """
    if not (serv_class and serv_class.servers):
        return True

    if serv_class.skip_prod_copy:
        log(' skip_prod_copy set - skipping')
        return True

    okay = True
    for host in serv_class.servers:
        if host in servers_done:
            continue
        servers_done.add(host)
        if not _copy_local_to_remote(ssl_mgr, host):
            okay = False
    return okay

def _post_copy_command(ssl_mgr:"SslMgr"):
    """
    After certs are copied run any post_copy_cmd programs
    post_copy_cmd ~ [[host1, command1], [host2, command2], ..]
    Each command is run locally and passed host as argument
    Config check validates post_copy_cmd is either empty/None
    or list of items - each item a list of 2 [host, cmd] elems
    NB
      command failures are treated as non-fatal. Log and continue
      We dont want one failure to prevent the remainder of things being done.
    """
    logs = ssl_mgr.logs
    num_fails = 0

    if not ssl_mgr.opts.post_copy_cmd:
        return 0

    for (host, cmd) in ssl_mgr.opts.post_copy_cmd:
        pargs = [cmd, host]
        if ssl_mgr.opts.debug:
            logs(f'  debug: {pargs}')
        else:
            logs(f' Post Copy : [{host}, {cmd}]')
            [retc, _sout, _serr] = run_prog(pargs, log=ssl_mgr.log)
            if retc != 0:
                logs(f'Error: {pargs} - continuing')
                num_fails += 1
    return num_fails

def certs_to_production(ssl_mgr:"SslMgr"):
    """
    1) Keys/certs are copied to prod_cert_dir defined in ssm-mgr.conf.
     - saved to: <prod_cert_dir>/<apex_domain>/<service>/xxx.pem
     - apex_domain = group_name

    2) Copy to all other servers (skipping _self)
    """
    logs = ssl_mgr.logs
    #
    # Check if any changes
    #
    changes = ssl_mgr.changes
    if changes.any.cert_changed or changes.any.dns_changed or ssl_mgr.opts.certs_to_prod:
        logs('ssl-mgr: Changes => copy certs/dns to production')
    else:
        return True

    #
    # copy everything in prod_cert_dir on this machine
    #
    if not _copy_local_prod(ssl_mgr):
        return False

    #
    # List of server types we know about
    #
    server_types = ('smtp', 'imap', 'web', 'other')
    servers_done = set()
    for stype in server_types:
        server = getattr(ssl_mgr.opts, stype)
        if not _copy_to_server(ssl_mgr, server, servers_done, logs):
            return False

    #
    # Run any post copy commands
    #
    logs('Running post_copy_cmd:')
    num_fails = _post_copy_command(ssl_mgr)
    if num_fails > 0:
        logs(f'Warning: post copy commands had {num_fails}')

    return True
