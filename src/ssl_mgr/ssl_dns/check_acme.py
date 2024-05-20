# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
DNS tools
"""
# pylint: disable=invalid-name,line-too-long,too-many-locals
import time
from .dns import dns_serial, dns_query

def _wait_time_by_try(num_tries:int) -> int:
    """
    Returns seconds to wait
    """
    if num_tries < 3:
        return 5

    if num_tries < 5:
        return 10

    if num_tries < 10:
        return 30

    if num_tries < 20:
        return 60

    if num_tries < 40:
        return 90

    return 120

def check_acme_challenges(ssl_dns:'SslDns', challenges:[str]):
    """
    Wait until all authoritative servers have the correct acme-chellenge RR
    challenges is list of (domain, validation) pairts.
    where each domain is the apex domain or any subdomain of it.
    For wildcards strip off leading .*
    ssl_dns.domain must be the apex domain of this domain
    Returns True if all servers up to date.
    Mathod:
        - check primary domain has all the challenges - just a sanity check.
        - get SOA serial number
        - check all nameservers (authoritative plus xtra) have correct serial
    """
    #
    # Pre check delay
    #
    check_delay = ssl_dns.check_delay
    if check_delay > 0:
        ssl_dns.logs(f'check_acme_challenge pre check delay: {check_delay}')
        time.sleep(check_delay)

    #
    # Confirm primary has the challenges
    # (should never fail)
    #
    primary_ok = check_primary_challenges(ssl_dns, challenges)
    if not primary_ok:
        # ug - wait a minute and try again .. should not happen
        time.sleep(60)
        primary_ok = check_primary_challenges(ssl_dns, challenges)

    if not primary_ok:
        ssl_dns.logs('dns check_acme : primary missing challenges! Should never happen FATAL')
        return False

    #
    # Check all nameservers
    #
    updated = check_nameservers_updated(ssl_dns)
    return updated

def check_primary_challenges(ssl_dns, challenges):
    """
    Confirm that primary server has all current challanges
    challenges is a list of (domain, validation) pairs
    """
    ssl_dns.logs('  check_acme : check primary has challenges')
    primary = ssl_dns.primary_resolver
    num_challenges = len(challenges)
    num_matched = 0
    for (domain, validation) in challenges:
        query = f'_acme-challenge.{domain}.'
        rrs = dns_query(primary, query, 'TXT')
        if rrs:
            for rr in rrs:
                if validation in rr:
                    num_matched += 1
                    break

    if num_matched == num_challenges:
        ssl_dns.logs('  primary up to date')
        return True
    return False

def check_nameservers_updated(ssl_dns):
    """
    Check each nameserver has current serial
    """
    ssl_dns.logs('  check_acme : checking nameservers updated')
    #
    # Get primary serial
    #
    apex_domain = ssl_dns.apex_domain
    primary = ssl_dns.primary_resolver
    serial_primary = dns_serial(primary, apex_domain)

    #
    # Check all resolvers have correct serial
    #
    wait_time = 5
    max_tries = 50      # approx 1 hour
    all_done = False
    pending = [ns for (ns, resolver) in ssl_dns.resolvers.items()]
    done = []

    #
    # Each "try" is one check of every authorized plus xtra name servers
    #
    num_tries = 0

    ssl_dns.log('Checking nameservers for current acme-challenges')
    while not all_done:
        for (ns, resolver) in ssl_dns.resolvers.items():
            #
            # check all the authorized name servers
            #
            if ns in done :
                continue

            serial = dns_serial(resolver, apex_domain)
            if serial :
                if serial == serial_primary:
                    done.append(ns)
                    pending.remove(ns)
                    ssl_dns.log(f' {ns} ok')
            else:
                ssl_dns.logs(f' ns {ns} failed to return serial')

        if len(pending) < 1 :
            all_done = True
            break

        ssl_dns.logs(f' pending: {pending} try {num_tries}')
        num_tries += 1
        if num_tries >= max_tries:
            ssl_dns.logs(f'Err: nameserver(s) not updated {apex_domain} : {pending}')
            return False

        wait_time = _wait_time_by_try(num_tries)
        ssl_dns.logs(f' wait: {wait_time}')
        time.sleep(wait_time)

    return True
