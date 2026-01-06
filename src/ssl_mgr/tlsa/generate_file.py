# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Generate TLSA resource record file(s)
"""
# pylint: disable=too-many-locals,invalid-name
import os

from ssl_mgr.utils import Log
from ssl_mgr.utils import write_path_atomic
from ssl_mgr.dns_base import (SslDns, dns_tlsa_record_format)
from ssl_mgr.crypto_cert import SslCert

from .tlsa_info import TlsaItem


def _match_type_to_hash_name(match_type: int) -> str:
    """
    dane tls match:
        0 => exact match (not used by us)
        1 => SHA256
        2 => SHA512
    """
    hash_name: str = ''
    if match_type == 1:
        hash_name = 'SHA256'

    elif match_type == 2:
        hash_name = 'SHA512'

    return hash_name


def _tlsa_update_one(cert: SslCert, ssl_dns: SslDns) -> list[str]:
    """
    Make file with tlsa records
    """
    dns_rr: list[str] = []

    logger = Log()
    logs = logger.logs
    ssl_svc = cert.svc
    dane_tls = ssl_svc.dane_tls

    if not dane_tls:
        return dns_rr

    apex_domain: str = ssl_dns.apex_domain

    #
    # ssl_dns.mx_hosts is dict of (prio, host)
    # pull off subdomains into 'mx_hosts' list
    # NB each host has trailing period
    #
    mx_hosts: list[str] = []
    for (_prio, mx_host) in ssl_dns.mx_hosts.items():
        mx_hosts.append(mx_host)

    #
    # Make list of san domains (with traling period same as mx_hosts)
    #
    # san_list: list[str] = ssl_svc.x509.sans
    san_list: list[str] = []
    for dom in ssl_svc.x509.sans:
        if not dom.endswith('.'):
            dom += '.'
        san_list.append(dom)

    for one in dane_tls:
        #
        # Gather the DANE info
        #  - for mail add tlsa for each MX otherwise for each san domain
        # We determine subdomains based on port - we also allow config to
        # set the type to MX or SANS in the 6th position of dane_tls list.
        # The default is to use X509 SANS domains unless tls
        # port is 25 - in which case MX hosts are used instead.
        #
        subdomains = san_list

        if one.subtype.upper() == 'MX' or one.port == 25:
            subdomains = mx_hosts

        hash_name = _match_type_to_hash_name(one.match_type)

        tlsa_data: str = ''
        if one.selector == 0:
            tlsa_data = cert.get_cert_hash(hash_name)
        else:
            tlsa_data = cert.get_pubkey_hash(hash_name, serialize_fmt="DER")

        if not tlsa_data:
            logs(f' {apex_domain} tlsa: bad or missing cert - skipping')
            continue

        #
        # the record data for TLSA has:
        #    usage selector match_type cert_or_key_hash
        # For convenience we let
        #   tlsa_key = usage selector match_type
        #
        tlsa_key = f'{one.usage} {one.selector} {one.match_type}'
        tlsa_rdata = dns_tlsa_record_format(tlsa_key, tlsa_data)

        #
        # Apex domain
        #
        rec = f'_{one.port}._{one.proto}.{apex_domain}. IN TLSA {tlsa_rdata}'
        dns_rr.append(rec)

        #
        # Subdomains
        #

        # loop on apex + mx domains
        #
        for subdomain in subdomains:
            if subdomain != apex_domain:
                tls_key = f'_{one.port}._{one.proto}.{subdomain}'
                rec = f'{tls_key} IN TLSA {tlsa_rdata}'
                dns_rr.append(rec)
    return dns_rr


def tlsa_generate_file(tlsa_item: TlsaItem) -> bool:
    """
    Generate tlsa RR file for certificates for one service.
    Does it for one lname = curr or next.
    Creates the resource records file
    See tls_update_domain
    """
    if not tlsa_item.dane_tls:
        # nothing to do
        return True

    logger = Log()
    logs = logger.logs

    apex_domain = tlsa_item.apex_domain
    lname = tlsa_item.lname
    db = tlsa_item.db

    db_name = db.db_names[lname]
    cert = tlsa_item.cert[db_name]
    if not cert:
        txt = f'{apex_domain} : {tlsa_item.svc_name} {tlsa_item.lname}'
        logs(f'Error: tlsa update: missing cert {txt}')
        return False

    dns_rr = []
    dns_rr = _tlsa_update_one(cert, tlsa_item.ssl_dns)

    #
    # save tlsa records file in own db dir
    #
    tls_file = 'tlsa.rr'
    db_dir = db.db_dir
    tls_path = os.path.join(db_dir, db_name, tls_file)

    # Gather the data to write
    rr_data = f';;\n;; tlsa {apex_domain} {tlsa_item.svc_name} {db_name}\n;;\n'
    rr_data += '\n'.join(dns_rr) + '\n'

    okay = write_path_atomic(rr_data, tls_path)

    if not okay:
        logs(f'Error: writing {tls_path}')
        return False

    return True
