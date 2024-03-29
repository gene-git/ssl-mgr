# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
DNS tools
"""
# pylint: disable=invalid-name,line-too-long
import time
from .dns import dns_query

def _wait_time_by_try(num_tries:int) -> int:
    """
    Returns seconds to wait
    """
    if num_tries < 3:
        return 1.5

    if num_tries < 5:
        return 3

    if num_tries < 10:
        return 5

    if num_tries < 20:
        return 5

    return 5

def check_acme_challenge(ssl_dns:'SslDns', domain:str, validation:str):
    """
    Wait until all authoritative servers have the correct acme-chellenge RR
    domain is the primary domain or any subdomain of that.
    for wildcarda strip off the leading .*
    ssl_dns.domain must be the apex domain of this domain
    """
    if not domain.endswith(ssl_dns.apex_domain):
        print(f'Error: {domain} must be under apex {ssl_dns.apex_domain}')
        return False
    query = f'_acme-challenge.{domain}.'
    wait_time = 5
    max_tries = 120

    num_ns = len(ssl_dns.auth_ns)
    num_valid = 0
    all_done = False
    checks = {}

    #
    # Each "try" is a check of every authorized name server
    #
    num_tries = 0

    while not all_done:
        for (ns, resolver) in ssl_dns.resolvers.items():
            if ns in checks and checks[ns]:
                continue

            #
            # check all the authorized name servers
            #
            rrs = dns_query(resolver, query, 'TXT')
            if rrs :
                for rr in rrs:
                    if validation in rr:
                        checks[ns] = True
                        num_valid += 1
            #else:
            #    checks[ns] = False

        if num_valid == num_ns:
            all_done = True
            break

        num_tries += 1
        if num_tries >= max_tries:
            print(f'Err: Failed to validate acme challeng {domain}')
            return False

        wait_time = _wait_time_by_try(num_tries)
        time.sleep(wait_time)
    return True
