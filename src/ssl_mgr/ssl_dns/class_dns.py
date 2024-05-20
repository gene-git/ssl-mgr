# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
DNS tools
"""
# pylint: disable=invalid-name,too-many-instance-attributes
# pylint: disable=too-many-arguments
import netaddr
from utils import get_certbot_logger

from .dns import dns_resolver
from .dns import auth_nameservers
from .dns import dns_query
from .check_acme import check_acme_challenges

def _mx_host_dict(mx_hosts_raw:[str]):
    """
    Map list of "prio host" to dictionary
     - key = prio
     - val = host
    """
    mx_hosts = {}
    for item in mx_hosts_raw:
        (prio, host) = item.split()
        mx_hosts[prio] = host
    return mx_hosts

def _is_valid_ip(address):
    """ check if ip or domain name """
    if netaddr.valid_ipv4(address) or netaddr.valid_ipv6(address):
        return True
    return False

class SslDns:
    """
    dns class for validating when dns has flushed acme validation TXT records
    Each instance is associated with one domain name for which we will be
    checking it's authoritative name servers for the challenge records.
    """
    def __init__(self, apex_domain, dns_primary, dns_port, check_delay, check_xtra_ns):
        """
        domain
            domain whose authoritative NS will be queried to confirm DNS acme challenges
            are flushed to all the NS

        dns_primary:dns_port
            dns server that can provide dns as seen from internet
            used to get a list of authoritative nameservers for 'apex_domain'
            IPs are looked up using standard dns recursive stub resolver.
        We initialize:
            resolver = standard default system caching resolver
            ns_reszolvers = dictionary of resolvers using each authoritative name server
        """
        self.apex_domain = apex_domain
        self.primary = dns_primary
        self.port = dns_port
        self.auth_ns = []
        self.resolvers = {}
        self.checks = {}
        self.mx_hosts = None
        #self.stub_resolver = None

        self.check_delay = -1
        self.xtra_ns = []

        self.logger = get_certbot_logger()
        self.logs = self.logger.logs
        self.log = self.logger.log
        self.logv = self.logger.logv

        if check_delay and check_delay > 0:
            self.check_delay = check_delay
            #self.log(f'ssl_dns: delay : {check_delay}')

        #
        # system default name server
        #
        self.stub_resolver = dns_resolver()

        #
        # get IP of primary if passed in as domain
        #
        dns_ips = [dns_primary]
        if not _is_valid_ip(dns_primary):
            dns_ips = dns_query(self.stub_resolver, dns_primary, 'A')

        self.primary_resolver = dns_resolver(dns_ips, dns_port)

        # get the list of authoritative name servers
        self.auth_ns = auth_nameservers(apex_domain, self.primary_resolver, self.stub_resolver)

        # add any extra nameserver ips to check
        if check_xtra_ns:
            #self.log(f'ssl_dns: xtra_ns : {check_xtra_ns}')
            for xns in check_xtra_ns:
                if _is_valid_ip(xns):
                    self.xtra_ns.append(xns)
                else:
                    dns_ips = dns_query(self.stub_resolver, xns, 'A')
                    self.xtra_ns += dns_ips

        #
        # Set up resolvers without caching for each auth ns and each xtra_ns
        #  - auth_ns : name:ip
        #  - xtra_ns:  ip:ip
        #
        for (ns, ip) in self.auth_ns.items():
            self.resolvers[ns] = dns_resolver(ip, port=53)
            self.checks[ns] = False

        for ip in self.xtra_ns:
            ns = ip
            if ns not in self.resolvers:
                self.resolvers[ns] = dns_resolver(ip, port=53)
                self.checks[ns] = False

        if self.primary_resolver and self.apex_domain:
            self.mx_hosts = dns_query(self.primary_resolver, self.apex_domain, 'MX')

        #
        # mx_hosts = ['10 a.com', '20 b.com' ..]
        #  => {'10' : 'a.com', '20' : 'b.com', ..]
        #
        if self.mx_hosts:
            self.mx_hosts = _mx_host_dict(self.mx_hosts)

    def query(self, query, rr_type):
        """
        Use all the auth ns to make query and return list of results
        """
        res = dns_query(self.stub_resolver, query, rr_type)
        return res

    def query_primary(self, query, rr_type):
        """
        Use all the auth ns to make query and return list of results
        """
        res = dns_query(self.primary_resolver, query, rr_type)
        return res

    def query_ns(self, query, rr_type):
        """
        Use all the auth ns to make query and return list of results
        """
        results = {}
        for (ns, resolver) in self.resolvers.items():
            results[ns] =  dns_query(resolver, query, rr_type)
        return results

    def check_acme_challenges(self, challenges:[str]):
        """
        Check that every auth name server has correct acm-challenge
        domain must be apex or ubdomain of apex_domain - as apex
        has the name servers
        """
        return check_acme_challenges(self, challenges)
