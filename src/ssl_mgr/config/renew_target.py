# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Given Original expiration days, Current expiration
Return the days remaining to renew
If remaining days is <= 0 then its tiem to renew now.
"""


def _pw_linear(x0, y0, x1, y1, x) -> float:

    y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return y


def _func_lookup(func: list[tuple[float, float]], orig: float) -> float:
    """
    func is the target function - list of tuple (x, y) with x original expiration days
    and y is the target number of days to renew - any time days to expiration is <= target renew
    then go ahead and renew.

    Function is piecw wise linear on interior. Lower bound is the first element.
    Upper bound uses the percent of the last element (longest expiration) and applies it
    for any expiration longer than the last element.
    """

    num = len(func)
    if num < 1:
        return 0.0

    if orig <= func[0][0]:
        return func[0][1]

    if orig >= func[num - 1][0]:
        frac = func[num - 1][1] / func[num - 1][0]
        return frac * orig

    for i in range(num - 2, 0, -1):
        lo = func[i]
        hi = func[i + 1]

        if orig >= lo[0]:
            days = _pw_linear(lo[0], lo[1], hi[0], hi[1], orig)
            return days

    return -1


def renew_target(renew_func: list[tuple[float, float]],
                 rand_adj_func: list[tuple[float, float]], orig: float) -> tuple[float, float]:
    """
    Given the renew and random adjustment functinos and the original expiration in days
    returns the applicable target days to renew at along with it's targeted adjustment.
    """

    renew_days: float = 0.0
    adj_days: float = 0.0

    renew_days = _func_lookup(renew_func, orig)
    adj_days = _func_lookup(rand_adj_func, orig)

    return (renew_days, adj_days)
