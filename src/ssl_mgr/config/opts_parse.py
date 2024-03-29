# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  ssl-mgr application command line options
  options:
   - Application works on one or more group-service pairs.
   - Doing multiples, allows a single DNS update which is more efficient.
   - group services pairs are passedon command line:
     group[:service1,service_2,...] group2[:...
    Services are required - special service 'ALL' means all available services will be processed
"""
import argparse
from .opts import get_available_options

def _split_group_services(grp_svcs: str) -> (str, [str]):
    """
    Split group[:svc1, svc2,...]
     - service must be given - or use 'all'
    """
    services = []
    gs_split = grp_svcs.partition(':')
    group = gs_split[0]
    services = gs_split[2]
    if services:
        services = services.split(',')
    else:
        services = None
    return (group, services)

def _parse_groups_services(all_grps_svcs:[str]) -> [(str, [str])]:
    """
    Parse list of grp_svcs from command line
        grp1:svc1,svc2,... grp2:svc1,svc2,...
    Return dictionary keyed by group name => list of service names
       {grp1 : [svc1, svc2, ...],
        grp2 : [svc1. svc2, ...].
        ...
       }
    """
    if not all_grps_svcs:
        return None

    group_svcs = {}
    for grp_svcs in all_grps_svcs:
        (group, svcs) = _split_group_services(grp_svcs)
        if not svcs:
            continue
        if group not in group_svcs:
            group_svcs[group] = []
        group_svcs[group] += svcs

    return group_svcs

def parse_options(defaults:dict) -> dict:
    """
    Parse command line and return dictionary of options
      Support for dev mode which adds more options.
      ssl-mgr [dev] (dev options)
    """
    # pylint: disable=too-many-locals

    #
    # Get available options
    #
    (prog, desc, epilog, argv, avail_opts) = get_available_options(defaults)

    #
    # Parse options used
    #
    par = argparse.ArgumentParser(description=desc, epilog=epilog, prog=prog)

    for opt in avail_opts:
        opt_keys, kwargs = opt
        opt_s = opt_keys[0]
        if len(opt_keys) > 1 and opt_keys[1]:
            opt_l = opt_keys[1]
            par.add_argument(opt_s, opt_l, **kwargs)
        else:
            par.add_argument(opt_s, **kwargs)

    #
    # Save as dictionary
    #
    parsed = par.parse_args(argv)
    opt_dict = {}
    if parsed:
        for (opt, val) in vars(parsed).items():
            opt_dict[opt] = val

    #
    # Positional args are list of [groups:services, ...]
    #
    grps_svcs = opt_dict.get('grps_svcs')
    opt_dict['grps_svcs'] = defaults['grps_svcs']
    if grps_svcs:
        opt_dict['grps_svcs'] = _parse_groups_services(grps_svcs)

    return opt_dict
