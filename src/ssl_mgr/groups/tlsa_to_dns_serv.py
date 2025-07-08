# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Generate TLSA resource record file(s)
"""
# pylint: disable=too-many-locals
from dns_base import dns_zone_update
from utils import Log

from ._group_data import GroupData


def tlsa_copy_to_dns_serv(group: GroupData):
    """
    - Copy the tlsa record file for apex domain
      to dns server
      It is then included in zone files and
      ready to be signed and pushed out.
    """
    #
    # save tlsa records file
    #
    tls_path = group.tlsa_path
    opts = group.opts

    logger = Log()
    logs = logger.logs
    logsv = logger.logsv

    logsv(f'copy tlsa for {group.apex_domain} to dns_server dirs')

    #
    # 1) Did the tlsa file change
    # 2) Is the dns version of file up to date
    #
    # Here, always Copy tls RR to zone include dir - leave signing/push to
    # application top level - it will wait for all domains before pushing dns.
    # and will only push if there was some change
    #
    if not (opts.dns and opts.dns.tlsa_dirs):
        logs('Warning: tlsa_copy_to_dns_serv missing tlsa_dirs - skipped')
        return False

    isok = dns_zone_update(tls_path,
                           opts.dns.tlsa_dirs,
                           debug=opts.debug)

    return isok
