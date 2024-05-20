# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
DNS tools
"""
# pylint: disable=invalid-name,line-too-long
import dns
import dns.resolver

def auth_nameservers(apex_domain:str,
                     primary_resolver:dns.resolver.Resolver,
                     stub_resolver:dns.resolver.Resolver):
    """
    Return a list of authoritative NS for apex_domain.
      server - if set, use this server to query for NS
      dns_port   - if set use this port
      stub_resolver = used to look IPs of each NS
    NB - this should be the apex_domain.
         e.g. example.com and not www.example.com
         We dont walk back from www.example.com to find NS for example.com
    """
    response = primary_resolver.resolve(apex_domain, 'NS')
    ns_list = {}
    if response.rrset:
        for rec in response.rrset:
            this_ns = rec.to_text()
            # primary then stub
            ips = dns_query(primary_resolver, this_ns, 'A')
            if not ips:
                ips = dns_query(stub_resolver, this_ns, 'A')

            if ips:
                ns_list[this_ns] = ips[0]

    return ns_list

def dns_resolver(server:str=None, port:int=53, cache=False):
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

def dns_query(resolver, query, rr_type):
    """
    This uses stub resolver
      - strip quotes around any response (TXT records)
    """
    try:
        res = resolver.resolve(query, rr_type)
    except dns.exception.DNSException:
        return None

    rrs = []
    if not res:
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

def dns_serial(resolver, apex_domain):
    """
    Check resolvert for SOA serial of apex_domain
    """
    try:
        res = resolver.resolve(apex_domain, 'SOA')
    except dns.exception.DNSException:
        return None

    serial = None
    if res and res.rrset:
        # only 1 SOA record
        serial = res.rrset[0].serial
    return serial
