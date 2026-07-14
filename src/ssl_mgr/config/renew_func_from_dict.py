# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Config holds a dictionary containing possible values for fixed
original cert expiration in days. The values for each is the time to renew
in days before expiration.

For example:
        target_300: float = 60.0
        target_120: float = 45.0
        target_90: float = 30.0
        target_60: float = 20.0
        target_45: float = 10.0
        target_10: float = 5.0
        target_6: float = 2.0
        target_2: float = 1.0
        target_1: float = 0.5

        # random variability days (0 means no variability)
        rand_adj_300: float = 0.0
        rand_adj_120: float = 0.0
        rand_adj_90: float = 0.0
        rand_adj_60: float = 0.0
        rand_adj_45: float = 0.0
        rand_adj_10: float = 0.0
        rand_adj_6: float = 0.0
        rand_adj_2: float = 0.0
        rand_adj_1: float = 0.0

We add the values as above and allow any to be over written by any positive value
Only keys above are processed.
"""
import bisect
from operator import itemgetter


def _float_is_same(x0: float, x1: float, eps: float) -> bool:
    if x1 - eps <= x0 <= x1 + eps:
        return True
    return False


def _insert_one(first_elem: itemgetter, pair: tuple[float, float], all_items: list[tuple[float, float]]):
    """
    Add 'pair' to the list - overwrtites any existing element if found
    """
    idx = bisect.bisect_left(all_items, pair[0], key=first_elem)

    if idx < len(all_items) and _float_is_same(all_items[idx][0], pair[0], 0.1):
        all_items[idx] = pair
    else:
        bisect.insort(all_items, pair, key=first_elem)


def renew_func_from_dict(data: dict[str, float],
                         target: list[tuple[float, float]],
                         rand_adj: list[tuple[float, float]]):
    """
    Process the data into sorted arrays.
    Dups are ignopred.
    """
    #
    # Create the defaults
    #
    def_target = [
            (0, 0.25),
            (1, 0.5),
            (2, 1),
            (5, 2),
            (10, 5),
            (45, 10),
            (60, 20),
            (90, 30),
            (120, 45),
            (300, 60),
            ]

    def_rand_adj = [
            (0, 0.0),
            (1, 0.0),
            (2, 0),
            (5, 0),
            (10, 0),
            (45, 0),
            (60, 0),
            (90, 0),
            (120, 5),
            (300, 0),
            ]

    target[:] = def_target
    rand_adj[:] = def_rand_adj

    first_elem = itemgetter(0)

    for (key, value) in data.items():
        if key.startswith('target_'):
            expiry = float(key.replace('target_', ''))
            pair = (expiry, value)
            _insert_one(first_elem, pair, target)

        elif key.startswith('rand_adj_'):
            expiry = float(key.replace('rand_adj_', ''))
            pair = (expiry, value)
            _insert_one(first_elem, pair, rand_adj)

    target.sort()
    rand_adj.sort()
