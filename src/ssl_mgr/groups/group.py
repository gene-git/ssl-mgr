# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  group (ca or apex domain) class
"""
# pylint: disable=too-many-instance-attributes
# pylint disable=invalid-name

from .group_tasks import group_to_production
from .group_tasks import execute_tasks
from .group_data import GroupData


class SslGroup(GroupData):
    """
    Group is either a 'CA' or an 'Apex Domain'
    It holds a collection of services.
     - Called from ssl_mgr
     - grp_name:svcs are from command line options and passed in here
    """
    # def __init__(self, grp_name: str, svcs: list[str], opts: SslOpts):
    #     super().__init__(grp_name, svcs, opts)

    def do_tasks(self) -> bool:
        """
        Run whatever been tasked to do
        """
        return execute_tasks(self)

    def to_production(self, prod_group_dir: str) -> bool:
        """
        Copy certs/keys, tlsa file -> <prod_group_dir>/<service>/xxx.pem
        ssl_mgr requests this if all groups comeplete without error
            we do not do it here even if this group has no errors
        """
        return group_to_production(self, prod_group_dir)

    def cleanup(self):
        """
        Do we need to ask each service to clean itself?
        """
