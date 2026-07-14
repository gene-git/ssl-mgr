# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Data used for when to renew decision

Default renew targets

    Issue Expire    Target Left     Renew After     Check Frequency
    90 -            30              60              1 / day
    60 - 89         20              40 - 79         1 /day
    45 - 59         10              35 - 49         1 /day
    10 - 44          5               5 - 44         1 /day
     6 -  9          2               4 -  7         1 /day
     2 -  5          1               1 -  4         2 /day
          1          0.5                  0.5       2 /day
"""
# pylint: disable=too-many-instance-attributes
import random

from .renew_func_from_dict import renew_func_from_dict
from .renew_target import renew_target


class RenewInfo:
    """
    When to renew
    """
    def __init__(self):
        #
        # target function is a list of (orig_expiry, days_to_renew)
        # rand_adj = list of (orig_expiry, random adjustment days)
        # Lower bound fixed at (0, 0.25)
        # Upper bound for expiry >= 300 is 20% of expiry
        #
        self.renew_func: list[tuple[float, float]] = []
        self.rand_adj_func: list[tuple[float, float]] = []

    def from_dict(self, data_dict: dict[str, float]):
        """
        Extract data from dictionary
        """
        renew_func_from_dict(data_dict, self.renew_func, self.rand_adj_func)

    def target(self, issue_days: float) -> tuple[float, float, float]:
        """
        Return target in days to use for cert with original expiration
        of "issue_days"

        Input:
            issue_days (float)
                Certificate expiraion days at issue (90, 45, 6, ...)

        Return:
            tuple[target: float, adjust_size: float, adjust_used: float]
            Target renewal expiration in days and random adjustment if requested.
        """
        target: float = 1.0
        rand_adj_size: float = 0.0
        rand_adj_used: float = 0.0

        (target, rand_adj_size) = renew_target(self.renew_func, self.rand_adj_func, issue_days)
        if rand_adj_size > 0:
            rand_adj_used = _rand_adj(rand_adj_size)

        return (target, rand_adj_size, rand_adj_used)

    def renew_decision(self, expiry_at_issue: float, expiry: float
                       ) -> tuple[bool, float, float]:
        """
        Input:
            expiry_at_issue (float):
                expiry days at issue date

            expiry(float):
                expiry days now

        Returns:
            tuple[is_renew_time: bool, days_to_renew: float, rand_adj: float]

                is_renew_time :
                    is true if time to renew

                days_to_renew:
                    days before its time to renew. No rand adjustment here.

                rand_adj:
                    if renewing, this is random adjustment size used to generate
                    any random adjustment. Not the adjustment used but the size.
                    from self.rand_adj_X

        """
        (target, adj_size, adj) = self.target(expiry_at_issue)

        days_to_renew = expiry - target
        is_renew_time = True
        if days_to_renew > adj:
            is_renew_time = False

        return (is_renew_time, days_to_renew, adj_size)


def _bounds_check(lo: float, hi: float, targ: float) -> float:
    """
    Make sure lo <= targ <= hi
    """
    target = min(hi, max(lo, targ))
    return target


def _rand_adj(size: float) -> float:
    """
    If size > 0 draw uniform random -size <= x <= size
    where size = min(size, max_size)

    Returns random adjustment to target in days with 1 decimal point
    """
    if size <= 0:
        return 0

    adj = random.uniform(-size, size)
    adj = round(adj, 1)
    return adj
