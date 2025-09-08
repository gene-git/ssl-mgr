# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
DNS primary
"""
# pylint: disable=too-many-locals

from utils import get_domain
from utils import Log
from config import SslOpts
from .class_dns import SslDns


def init_primary_dns_server(opts: SslOpts,
                            apex_domain: str,
                            ) -> SslDns:
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

    logger = Log()
    log = logger.logs

    #
    # Config provides dns server name/port
    # It can provide server name/port for one or
    # more specific domains.
    # If no server for the apex_domain, then
    # use the default server.
    #
    dns_primary = opts.dns_primary
    if not dns_primary or not isinstance(dns_primary, list):
        txt = 'init_primary_dns - missing dns_primary config section'
        log(txt)
        raise ValueError(txt)

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
        if not default_server:
            txt = 'Error: primary_dns no domain / default DNS server in config'
            log(txt)
            raise ValueError(txt)
        dns_server = default_server
        dns_port = default_port

    if not (dns_server and dns_port):
        txt = 'init_primary_dns - missing dns primary server / port'
        log(txt)
        raise ValueError(txt)

    #
    # Initialize dns to use
    #
    check_delay = opts.dns_check_delay
    xtra_ns = opts.dns_xtra_ns
    ssl_dns = SslDns(apex_domain, dns_server, dns_port, check_delay, xtra_ns)
    if not ssl_dns.okay:
        log('Error - DNS unavailable')
    return ssl_dns
