# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Convert data dictionary to class instance
"""
# pylint: disable=too-many-instance-attributes
from dataclasses import dataclass,field

@dataclass
class ConfSvcDep:
    """ servers depend on 1 or more of these to trigger restart """
    domain:str = None
    services:list[str] = field(default_factory=list)

@dataclass
class ConfDns:
    """ data for dns """
    #primary_server:str = None
    #primary_port:int = -1
    restart_cmd:str = None
    acme_dir:str = None
    tlsa_dirs:list[str] = field(default_factory=list)
    depends:list[str] = field(default_factory=list)
    svc_depends:list[ConfSvcDep] = field(default_factory=list)
    skip_prod_copy:bool = False

    def __getattr__(self, name):
        return None

@dataclass
class ConfServ:
    """ data for dns """
    servers:list[str] = field(default_factory=list)
    depends:list[str] = field(default_factory=list)
    svc_depends:list[ConfSvcDep] = field(default_factory=list)
    restart_cmd:str = None
    server_dir:str = None
    skip_prod_copy:bool = False     # testing or if server gets via NFS

def subdict_data_parse(valdict, this):
    """
    Parse sub dictionary into data class instance
    """
    for (subkey, subval) in valdict.items():
        if subkey == 'svc_depends':
            if not this.svc_depends:
                this.svc_depends = []

            svc_depends = this.svc_depends
            one_dep = ConfSvcDep()
            svc_depends.append(one_dep)

            for (domain, services) in subval :
                one_dep.domain = domain
                one_dep.services = services
        else:
            setattr(this, subkey, subval)

def dict_to_opts(opts:"SslOpts", data_dict:dict):
    """
    Map config data dictionary to SslOpts class instance
    """
    if not data_dict:
        return

    for (key, val) in data_dict.items():
        if isinstance(val, dict):
            if key in ('smtp', 'imap', 'web', 'other'):
                this = ConfServ()
                setattr(opts, key, this)

            elif key in ('dns'):
                this = ConfDns()

            elif key in ('group', 'grps_svcs'):
                setattr(opts, key, val)
                continue

            else:
                print(f'Config parser : uknown {key} {val}')
                # unknown ignore
                continue

            setattr(opts, key, this)
            subdict_data_parse(val, this)
        else:
            setattr(opts, key, val)
