# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
DNS primary
"""
from utils import get_domain
from .class_dns import SslDns

def init_primary_dns_server(opts:"SslOpts", apex_domain:str, log=print) -> SslDns :
    """
    Initialize dns server for current domain.
    this server is used to look up:
     - authoritative name servers
       needed when we checking if they all up to date
       with auth validation TXT record used by letsencrypt dns-01
     - MX hosts needed to create TLSA records.
    """
    if apex_domain == 'ca':
        # CA means our self sign CA - use our own domain
        apex_domain = get_domain()

    #
    # Config provides dns server name/port
    # It can provide server name/port for one or
    # more specific domains.
    # If no server for the apex_domain, then
    # use the default server.
    #
    dns_primary = opts.dns_primary
    if not dns_primary or not isinstance(dns_primary, list):
        log('init_primary_dns - missing dns_primary config section')
        return None

    #
    # Find domain specific or use default
    #
    dns_server = None
    dns_port = None
    default_server = None
    default_port = None
    for primary in dns_primary:
        server = primary.get('server')
        port = primary.get('port')
        domain = primary.get('domain')

        if domain.lower() in ('*', 'default'):
            default_server = server
            default_port = port

        if domain.lower() == apex_domain:
            dns_server = server
            dns_port = port
            break

    if not default_port:
        default_port = 53

    if not dns_server:
        if not default_server :
            log('Error - no domain or default DNS server in config')
            return None
        dns_server = default_server
        dns_port = default_port

    if not (dns_server and dns_port):
        log('init_primary_dns - missing dns primary server / port')
        return None

    #
    # Initialize dns to use
    #
    check_delay = opts.dns_check_delay
    xtra_ns = opts.dns_xtra_ns
    ssl_dns = SslDns(apex_domain, dns_server, dns_port, check_delay, xtra_ns)
    return ssl_dns
