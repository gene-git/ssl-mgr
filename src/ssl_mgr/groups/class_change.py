# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
 Track what changed
"""
# pylint: disable=too-many-instance-attributes, too-few-public-methods
from dataclasses import dataclass,field

@dataclass
class GroupChange:
    """ changes for one group"""
    svc_names:list[str] = field(default_factory=list)
    curr_cert_changed:bool = False                           # any service change
    next_cert_changed:bool = False                           # any service change
    cert_changed:bool = False                           # any service change
    tlsa_changed:bool = False
    dns_changed:bool = False
    depends:set = field(default_factory=set)

    def add_svc_name(self, svc_name):
        """ add one service name to list """
        self.svc_names.append(svc_name)
        self.cert_changed = True
        self.depends.add('cert')

    def set_tlsa_changed(self):
        """ mark tlsa/dns """
        self.tlsa_changed = True
        self.dns_changed = True
        self.depends.add('tlsa')
        self.depends.add('dns')

class GroupChanges:
    """ collects changes for all groups """
    def __init__(self):
        self.group = {}
        self.any = GroupChange()
        self.dns_domains_changed = []

    def add_group_change(self, group_name, group_change:GroupChange):
        """ add to list """
        self.group[group_name] = group_change

        if group_change.cert_changed:
            self.any.cert_changed = True

        if group_change.tlsa_changed:
            self.any.tlsa_changed = True

        if group_change.dns_changed:
            self.any.dns_changed = True

        if group_change.next_cert_changed:
            self.any.next_cert_changed = True

        if group_change.curr_cert_changed:
            self.any.curr_cert_changed = True

        if self.any.dns_changed:
            self.dns_domains_changed.append(group_name)

        if group_change.depends:
            self.any.depends.update(group_change.depends)
