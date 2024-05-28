# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Generate TLSA resource record file(s)
"""
# pylint: disable=too-many-locals
import os
from utils import open_file
from utils import write_path_atomic

def read_tlsa_info(fpath):
    """
    Read tlsa file and its time
    returns (data, st_atime, st_mtime)
    data is None if no such file
    """
    data = None
    nothing = (None, -1, -1)
    if not fpath:
        return nothing

    try:
        stat = os.stat(fpath)
    except OSError:
        return nothing

    fob = open_file(fpath, 'r')
    if not fob:
        return nothing

    data = fob.read()
    fob.close()

    return (data, stat.st_atime_ns, stat.st_mtime_ns)

def _merge_services(group_services, conf_services):
    """
    Merge services being worked on, group_services,
    with all services listed in config
    """
    if conf_services and group_services:
        services = list(set(conf_services).union(set(group_services)))
    else:
        if conf_services:
            services = conf_services
        else:
            services = group_services

    return services



def tlsa_update_domain(group:'SslGroup'):
    """
    Creates the final tlsa for apex domain (group)
    file consisting any nonempty :
      - <svc>/curr/tlsa.rr + <svc>/next/tlsa.rr

    Resuling tlsa file located in certs/apex_domain/tlsa.<apex_domain>
    contains combined tlsa for all services.
    Usually only one <svc> has a tlsa file for this domain
    time stamp should be the 'latest' of any tlsa.rr file
    Its fine to have multiple tlsa records - thats what happens
    during renewal (aka phase 1 roll) where 1 record has curr and other uses next

    This combined apex_domain tlsa file is copied to a dns directory
    for the apex_domain zone file, which pulls it into the zone file using $INCLUDE.
    During 1st phase of key roll, tlsa needs both curr and next tlsa records - this
    is normal for 'renew'. 2nd roll phase (called 'roll') rolls next to be new current
    and pushes out updates.

    ** Important **
    In order to ensure all tlsa files are kept we include union of all services from
    config file plus command line. Otheriwse running 1 service with no tlsa could
    just create empty group level one.
    """
    logs = group.logs
    opts = group.opts
    apex_domain = group.grp_name

    #
    # Create tlsa.<apex_domain> from all individual tlsa.rr files
    #
    apex_tlsa_path = group.tlsa_path

    phase = 'normal'
    if opts.roll:
        phase = 'roll next to curr'

    #
    # merge separate tlsa files into apex_domain tlsa file
    #  - since keys may be reused avoid duplicates across curr/next
    #  - make file time same as latest of all merged files
    #
    st_atime = 0
    st_mtime = 0

    #
    # Get union of services from config + opts. If none given on command line they will be same
    #
    opt_svc_names = group.opts.grps_svcs.get(apex_domain)
    conf_svc_names = group.opts.conf_grps_svcs.get(apex_domain)

    all_svc_names = _merge_services(opt_svc_names, conf_svc_names)

    # sets seem to sometimes changes order and trigger changes
    all_svc_names = sorted(all_svc_names)

    group_work_dir = group.db.work_dir

    #
    # tlsa_data_rows: used to track dups
    # Could also use this and join at the end before write
    #
    tlsa_data_rows = []
    apex_data = f';;\n;; TLSA {apex_domain} : phase = {phase}\n;;\n'
    for svc_name in all_svc_names:
        lnames = ['curr', 'next']

        for lname in lnames:

            this_tlsa_path = os.path.join(group_work_dir, svc_name, lname, 'tlsa.rr')
            (data, atime, mtime) = read_tlsa_info(this_tlsa_path)
            if data:
                if mtime > st_mtime:
                    st_mtime = mtime
                    st_atime = atime

                #
                # merge this file into apex file
                # Strip comments and comment dups
                #
                apex_data += f';;\n;; {svc_name} {lname}\n;;\n'
                data_rows = data.splitlines()
                for row in data_rows:
                    if row.startswith(';;'):
                        continue

                    this_row = ''
                    if row in tlsa_data_rows:
                        this_row += ';; '
                    this_row += row

                    tlsa_data_rows.append(this_row)
                    apex_data += this_row + '\n'

    if tlsa_data_rows:
        apex_data += '\n'
        okay = write_path_atomic(apex_data, apex_tlsa_path)
        if not okay:
            logs(f'Error: Failed to open {apex_tlsa_path}')
            return False

        # set file time
        if st_mtime > 0:
            os.utime(apex_tlsa_path, ns=(st_atime, st_mtime))
    else:
        group.log(f'tlsa: apex domain: {apex_domain} has no tlsa records')

    return True
