# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Generate TLSA resource record file(s)
"""
# pylint: disable=too-many-locals,invalid-name
import os
from utils import write_path_atomic
from ssl_dns import dns_tlsa_record_format

def _match_type_to_hash_type(match_type:int) -> str:
    """
    dane tls match:
        0 => exact match (not used by us)
        1 => SHA256
        2 => SHA512
    """
    hash_type = None
    if match_type == 1:
        hash_type = 'SHA256'
    elif match_type == 2:
        hash_type = 'SHA512'
    return hash_type

def _tlsa_update_one(cert:'SslCert', ssl_dns):
    """
    Make file with tlsa records
    """
    logs = cert.logs
    ssl_svc = cert.svc
    dane_tls = ssl_svc.dane_tls
    if not dane_tls :
        return None

    apex_domain = ssl_dns.apex_domain

    #
    # this is dict of (prio, host) where host has trailing period
    #
    mx_hosts = ssl_dns.mx_hosts

    dns_rr = []
    for item in dane_tls:
        [port, proto, usage, selector, match_type] = item
        hash_type = _match_type_to_hash_type(match_type)
        match selector:
            case 0:
                tlsa_data = cert.get_cert_hash(hash_type)
            case _:
                tlsa_data = cert.get_pubkey_hash(hash_type, serialize_fmt="DER")

        if not tlsa_data:
            logs(f' {apex_domain}  tlsa : bad or missing cert - skipping')
            continue

        #
        # the record data for TLSA has:
        #    usage selector match_type cert_or_key_hash
        # For convenience we let
        #   tlsa_key = usage selector match_type
        #
        tlsa_key = f'{usage} {selector} {match_type}'
        tlsa_rdata = dns_tlsa_record_format(tlsa_key, tlsa_data)
        rec = f'_{port}._{proto}.{apex_domain}. IN TLSA {tlsa_rdata}'
        dns_rr.append(rec)

        # loop on apex + mx domains
        for (_prio, mx_host) in mx_hosts.items():
            rec = f'_{port}._{proto}.{mx_host} IN TLSA {tlsa_rdata}'
            dns_rr.append(rec)

    return dns_rr

def tlsa_generate(service:'SslService', lname:str):
    """
    Generate tlsa RR file for certificates for one service.
    Does it for one lname = curr or next.
    Creates the resource records file(s)
    See tls_update_domain
    """
    if not service.svc.dane_tls:
        # nothing to do
        return True

    logs = service.logs
    db = service.db
    db_name = db.db_names[lname]
    cert = service.cert[db_name]
    if not cert:
        logs(f'Error: tlsa update: missing cert {service.svc_name} {lname}')
        return False

    dns_rr = []
    dns_rr = _tlsa_update_one(cert, service.ssl_dns)

    #
    # save tlsa records file in own db dir
    #
    apex_domain = service.apex_domain
    tls_file = 'tlsa.rr'
    db_dir = db.db_dir
    tls_path = os.path.join(db_dir, db_name, tls_file)

    # Gather the data to write
    rr_data = f';;\n;; tlsa {apex_domain} {service.svc_name} {db_name}\n;;\n'
    rr_data += '\n'.join(dns_rr) + '\n'

    okay = write_path_atomic(rr_data, tls_path)

    if not okay:
        logs(f'Error: writing {tls_path}')
        return False

    return True
