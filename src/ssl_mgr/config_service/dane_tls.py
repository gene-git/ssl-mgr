# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
TLSA data communiation class
"""
# pylint: disable=too-few-public-methods, too-many-instance-attributes
# pylint: disable=too-few-public-methods


class DaneTls:
    """
    Data for one dane tls item
    """
    def __init__(self):
        self.port: int = -1
        self.proto: str = ''
        self.usage: int = -1
        self.selector: int = -1
        self.match_type: int = -1
        self.subtype: str = ''

    def from_list(self, items: list[str | int]) -> bool:
        """
        Map config list format to our data.

        Config file has each item as a list :
           [port, proto, usage, selector, match_type, subtype]
        and subtype is optional
        """
        if not items:
            return True

        if len(items) < 5:
            print('Error: dane tls must have 5 or 6 elements')
            print(f'  : {items}')
            return False

        self.port = int(items[0])
        self.proto = str(items[1])
        self.usage = int(items[2])
        self.selector = int(items[3])
        self.match_type = int(items[4])
        if len(items) > 5:
            self.subtype = str(items[5])

        return True
