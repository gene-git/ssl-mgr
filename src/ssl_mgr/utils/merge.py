# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Merge tools
"""
from typing import (Any)


def merge_lists(list1: list[Any] | None,
                list2: list[Any] | None
                ) -> list[Any]:
    """
    Merge 2 lists (can be empty or None).

    Args:
        list1 (list[Any] | None):
            FIrst list to merge

        list2 (list[Any] | None):
            Second list

    Returns:
        list[Any]
        Resulting list of merging 2 input lists.

    """
    merged: list[str] = []

    # need merge
    if list1 and list2:
        merged = list(set(list1).union(set(list2)))
        return merged

    # no merge needed
    if list1:
        merged = list1

    elif list2:
        merged = list2

    return merged
