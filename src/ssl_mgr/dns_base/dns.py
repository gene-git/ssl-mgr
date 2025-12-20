# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
DNS tools
"""
# pylint: disable=invalid-name,line-too-long
import dns
import dns.resolver


def auth_nameservers(apex_domain: str,
                     primary_resolver: dns.resolver.Resolver,
                     stub_resolver: dns.resolver.Resolver
                     ) -> dict[str, str]:
    """
    Return a list of authoritative NS for apex_domain.
      server - if set, use this server to query for NS
      dns_port   - if set use this port
      stub_resolver = used to look IPs of each NS

    NB - this should be the apex_domain.
         e.g. example.com and not www.example.com
         We dont walk back from www.example.com to find NS for example.com
    """
    ns_list: dict[str, str] = {}

    try:
        response = primary_resolver.resolve(apex_domain, 'NS')

    except dns.exception.DNSException:
        # unable to get answer from DNS
        # means nds server is unavailable
        return ns_list

    if response.rrset:
        for rec in response.rrset:
            this_ns = rec.to_text()
            # primary then stub - if returns multiepl IPs
            # then we take the first. We want a 1-1 map
            # of nameserver -> ip (no alternates)
            ips = dns_query(primary_resolver, this_ns, 'A')
            if not ips:
                ips = dns_query(stub_resolver, this_ns, 'A')

            if ips:
                ns_list[this_ns] = ips[0]

    return ns_list


def dns_resolver(server: str | list[str] = '',
                 port: int = 53,
                 cache: bool = False
                 ) -> dns.resolver.Resolver:
    """
    initialize a resolver instance
    """
    resolver = dns.resolver.Resolver(configure=True)

    if server:
        if isinstance(server, list):
            resolver.nameservers = server
        else:
            resolver.nameservers = [server]
    resolver.port = int(port)

    # if asked for make it caching
    if cache:
        resolver.cache = dns.resolver.Cache()
    return resolver


def dns_query(resolver: dns.resolver.Resolver,
              query: str,
              rr_type: str
              ) -> list[str]:
    """
    This uses stub resolver
      - strip quotes around any response (TXT records)
    """
    rrs: list[str] = []

    try:
        res = resolver.resolve(query, rr_type)
    except dns.exception.DNSException:
        return rrs

    if not (res and res.rrset):
        return rrs

    if rr_type == 'A':
        ips = []
        for rec in res.rrset:
            ip = rec.address
            ips.append(ip)
        return ips

    for record in res.rrset:
        rrs.append(record.to_text().strip('"'))

    return rrs


def dns_serial(resolver: dns.resolver.Resolver,
               apex_domain: str) -> str:
    """
    Check resolvert for SOA serial of apex_domain
    """
    serial = ''

    try:
        res = resolver.resolve(apex_domain, 'SOA')
    except dns.exception.DNSException:
        return serial

    if res and res.rrset:
        # only 1 SOA record
        serial = res.rrset[0].serial
    return serial
