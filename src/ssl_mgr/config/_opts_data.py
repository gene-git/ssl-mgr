# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
ssl-mgr application command line options
options:
 - Application works on one or more group-service pairs.
 - Doing multiples, allows a single DNS update which is more efficient.
 - group services pairs are passedon command line:
   group[:service1,service_2,...] group2[:...

Services are required - special service 'ALL' means all
available services will be processed

configs are ServiceConf files locatd in:
  <top_dir>/conf.d/<group>/<service>

"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
from typing import (Any)
import os
from dataclasses import (dataclass, field)

from db import get_conf_dir

from .class_cainfo import CAInfos


#
# Data Classes for server and dns
#
@dataclass
class ConfSvcDep:
    """ servers depend on 1 or more of these to trigger restart """
    domain: str = ''
    services: list[str] = field(default_factory=list)


@dataclass
class ConfServ:
    """ data for dns """
    servers: list[str] = field(default_factory=list)
    depends: list[str] = field(default_factory=list)
    svc_depends: list[ConfSvcDep] = field(default_factory=list)
    restart_cmd: list[str] = field(default_factory=list)
    server_dir: str = ''
    skip_prod_copy: bool = False     # testing or if server gets via NFS

    def from_dict(self, data_dict: dict[str, Any]):
        """
        Parse dictionary and save values
        """
        for (key, val) in data_dict.items():
            if key == 'svc_depends':
                one_dep = ConfSvcDep()
                for (domain, services) in val:
                    one_dep.domain = domain
                    one_dep.services = services
                self.svc_depends.append(one_dep)

            elif key == 'restart_cmd' and isinstance(val, str):
                setattr(self, key, [val])
            else:
                setattr(self, key, val)


@dataclass
class ConfDns:
    """ data for dns """
    restart_cmd: list[str] = field(default_factory=list)
    acme_dir: str = ''
    tlsa_dirs: list[str] = field(default_factory=list)
    depends: list[str] = field(default_factory=list)
    # svc_depends: list[ConfSvcDep] = field(default_factory=list)
    skip_prod_copy: bool = False

    def __getattr__(self, name):
        return None

    def from_dict(self, data_dict: dict[str, Any]):
        """
        Parse dictionary and save values
        """
        for (key, val) in data_dict.items():
            if key == 'restart_cmd' and isinstance(val, str):
                setattr(self, key, [val])
            else:
                setattr(self, key, val)


def _top_dir(conf_dir: str) -> str:
    """
    top_dir has
      conf.d -  has ca-info.conf, directories with domains,  local ca configs
      certs  - has all certs and keys
    """
    top_dir = ''
    if conf_dir:
        top_dir = os.path.dirname(conf_dir)
    return top_dir


class SslOptsData:
    """
    Input options/config data for ssl manger.
    """
    def __init__(self):
        self.okay: bool = True
        self.conf_dir: str = get_conf_dir()
        self.top_dir: str = _top_dir(self.conf_dir)

        # options
        self.verb: bool = False
        self.debug: bool = False
        self.test: bool = False
        self.force: bool = False
        self.force_server_restarts: bool = False
        self.reuse_keys: bool = False     # reuse curr/{key,csr}
        self.dry_run: bool = False

        # task command options
        self.status: bool = False
        self.new_csr: bool = False
        self.new_keys: bool = False
        self.new_cert: bool = False
        self.renew_cert: bool = False
        self.refresh_cert: bool = False
        self.renew_cert_now: bool = False
        self.renew_expire_days: int = 30
        self.renew_expire_days_spread: int = 0
        self.copy_csr: bool = False
        self.clean_keep: int = 10
        self.clean_all: bool = False
        self.next_to_curr: bool = False
        self.cert: bool = False
        self.roll: bool = False
        self.min_roll_mins: int = 90
        self.certs_to_prod: bool = False
        self.dns_refresh: bool = False
        self.root_privs: bool = os.geteuid() == 0

        # config overrides these - may need longer delay
        self.dns_check_delay: int = 240
        self.dns_xtra_ns: list[str] = ['1.1.1.1', '8.8.8.8',
                                       '9.9.9.9', '208.67.222.222']

        self.post_copy_cmd: list[list[str]] = []

        self.groups: dict[str, list[dict[str, Any]]] = {}
        self.dns_primary: dict[str, list[dict[str, str | int]]] = {}

        # Current list
        self.dns: ConfDns = ConfDns()
        self.smtp: ConfServ = ConfServ()
        self.imap: ConfServ = ConfServ()
        self.web: ConfServ = ConfServ()
        self.other: ConfServ = ConfServ()

        # what to do tasks on
        self.grps_svcs: dict[str, list[str]] = {}

        self.sslm_auth_hook: str = '/usr/lib/ssl-mgr/sslm-auth-hook'

        self.prod_cert_dir: str = '/etc/ssl-mgr/prod-certs'
        self.logdir: str = '/var/log/ssl-mgr'

        #
        # Read ca-info.conf for Certificate authority info on all CAs
        #
        self.ca_infos = CAInfos(self.top_dir)

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None
