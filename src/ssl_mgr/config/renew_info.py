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


class RenewInfo:
    """
    When to renew
    """
    def __init__(self):
        # renew target days remaining time to cert expiration
        self.target_90: float = 30.0        # was renew_expire_days
        self.target_60: float = 20.0
        self.target_45: float = 10.0
        self.target_10: float = 5.0
        self.target_6: float = 2.0
        self.target_2: float = 1.0
        self.target_1: float = 0.5

        # random variability days (0 means no variability)
        self.rand_adj_90: float = 0.0       # was renew_expire_days_spread
        self.rand_adj_60: float = 0.0
        self.rand_adj_45: float = 0.0
        self.rand_adj_10: float = 0.0
        self.rand_adj_6: float = 0.0
        self.rand_adj_2: float = 0.0
        self.rand_adj_1: float = 0.0

    def from_dict(self, data_dict: dict[str, float]):
        """
        Extract data from dictionary
        """
        for (k, v) in data_dict.items():
            setattr(self, k, v)

    def target(self, issue_days: float) -> tuple[float, float, float]:
        """
        Return target in days to use for cer with original expiration
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

        if issue_days >= 90.0:
            self.target_90 = _bounds_check(1.0, 89.0, self.target_90)
            self.rand_adj_90 = _bounds_check(0.0, 5.0, self.rand_adj_90)

            target = self.target_90
            rand_adj_size = self.rand_adj_90

        elif issue_days >= 60.0:
            self.target_60 = _bounds_check(1.0, 59.0, self.target_60)
            self.rand_adj_60 = _bounds_check(0.0, 3.0, self.rand_adj_60)

            target = self.target_60
            rand_adj_size = self.rand_adj_60

        elif issue_days >= 45.0:
            self.target_45 = _bounds_check(1.0, 44.0, self.target_45)
            self.rand_adj_45 = _bounds_check(0.0, 2.0, self.rand_adj_45)

            target = self.target_45
            rand_adj_size = self.rand_adj_45

        elif issue_days >= 10.0:
            self.target_10 = _bounds_check(1.0, 9.0, self.target_10)
            self.rand_adj_10 = _bounds_check(0.0, 1.0, self.rand_adj_10)

            target = self.target_10
            rand_adj_size = self.rand_adj_10

        elif issue_days >= 6.0:
            self.target_6 = _bounds_check(1.0, 5.0, self.target_6)
            self.rand_adj_6 = _bounds_check(0.0, 1.0, self.rand_adj_6)

            target = self.target_6
            rand_adj_size = self.rand_adj_6

        elif issue_days >= 2.0:
            self.target_2 = _bounds_check(1.0, 1.9, self.target_2)
            self.rand_adj_2 = _bounds_check(0.0, 0.5, self.rand_adj_2)

            target = self.target_2
            rand_adj_size = self.rand_adj_2

        elif issue_days >= self.target_1:
            self.target_1 = _bounds_check(0.1, 0.9, self.target_1)
            self.rand_adj_1 = _bounds_check(0.0, 0.1, self.rand_adj_1)

            target = self.target_1
            rand_adj_size = self.rand_adj_1

        else:
            target = 0.25
            rand_adj_size = 0.0

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
