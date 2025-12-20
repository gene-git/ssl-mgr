# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
DNS tools
"""
# pylint: disable=invalid-name, too-many-instance-attributes
# pylint: disable=too-many-positional-arguments, too-many-arguments

from .dns import dns_query
from .check_acme import check_acme_challenges
from ._dns_data import SslDnsData


class SslDns(SslDnsData):
    """
    dns class for validating when dns has flushed acme validation TXT records
    Each instance is associated with one domain name for which we will be
    checking it's authoritative name servers for the challenge records.
    """
    def query(self, query: str, rr_type: str) -> list[str]:
        """
        Use all the auth ns to make query and return list of results
        """
        res = dns_query(self.stub_resolver, query, rr_type)
        return res

    def query_primary(self, query: str, rr_type: str) -> list[str]:
        """
        Use all the auth ns to make query and return list of results
        """
        res = dns_query(self.primary_resolver, query, rr_type)
        return res

    def query_ns(self, query: str, rr_type: str) -> dict[str, list[str]]:
        """
        Use all the auth ns to make query and return list of results
        """
        results: dict[str, list[str]] = {}
        for (ns, resolver) in self.resolvers.items():
            results[ns] = dns_query(resolver, query, rr_type)
        return results

    def check_acme_challenges(self, challenges: list[tuple[str, str]]) -> bool:
        """
        Check that every auth name server has correct acm-challenge
        domain must be apex or ubdomain of apex_domain - as apex
        has the name servers
        """
        return check_acme_challenges(self, challenges)
