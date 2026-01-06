# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
  service level tasks
"""
# pylint: disable=invalid-name
from ssl_mgr.crypto_cert import SslCert
from ssl_mgr.tlsa import (TlsaItem, tlsa_generate_file)
from ssl_mgr.utils import Log

from .copy_key_csr import copy_key_csr
from .service_time import (time_to_renew, log_cert_expiry, time_to_roll)
from ._service_data import ServiceData


def check_next_cert_changed(service: ServiceData) -> bool:
    """
    determine if next cert changed
    - at start no next and have next -> changed
    - time next/cert > time of cert at start
    - instead of time should we retrieve the fingerprint?
    """
    if service.next_cert_changed:
        return service.next_cert_changed

    if not service.next_cert_time:
        if service.state.next.cert_time:
            service.next_cert_changed = True

    elif service.state.next.cert_time:
        if service.state.next.cert_time > service.next_cert_time:
            service.next_cert_changed = True

    return service.next_cert_changed


def check_curr_cert_changed(service: ServiceData) -> bool:
    """
    determine if curr cert changed if:
      - at start no curr and have curr
      - time curr/cert != time of cert at start (should we enforce newer)
    - instead of time should we retrieve the fingerprint?
    """
    if service.curr_cert_changed:
        return service.curr_cert_changed

    if not service.curr_cert_time:
        if service.state.curr.cert_time:
            service.curr_cert_changed = True

    elif service.state.curr.cert_time:
        if service.state.curr.cert_time > service.curr_cert_time:
            service.curr_cert_changed = True

    return service.curr_cert_changed


def new_next(service: ServiceData) -> bool:
    """
    Make new 'next' dir
    """
    if not service.db.new_next():
        service.okay = False
    refresh_paths(service)
    service.next_cert_changed = True
    return service.okay


def new_key_pair(service: ServiceData) -> bool:
    """
    Make new key pairs
    - new always for 'next'
    """
    logger = Log()
    logs = logger.logs

    db_name = service.db.db_names['next']
    if not db_name:
        logs('    Error: cant make new keys next dir is missing')
        return False

    ssl_svc = service.svc
    db = service.db
    grp_name = service.grp_name
    service_name = service.svc_name
    opts = service.opts

    service.cert[db_name] = SslCert(db_name, ssl_svc,
                                    db, grp_name, service_name, opts)

    refresh_paths(service)
    if not service.state.next.privkey_ready:
        logs('    Error: Not ready to make privkey - unclear why')
        service.okay = False
        return False

    if not service.cert[db_name].new_key_pair():
        service.okay = False
        return False

    refresh_paths(service)
    service.next_cert_changed = True
    return True


def new_csr(service: ServiceData) -> bool:
    """
    Make new key pairs
     - new always for 'next'
     - since keys must come first, cert[db_name] must existo
     - should we confirmn?
    """
    logger = Log()
    logs = logger.logs

    if not service.state.next.csr_ready:
        logs('    Error: Make csr requires keys')
        service.okay = False
        return False

    lname = 'next'
    db_name = service.db.db_names[lname]
    if not service.cert[db_name].new_csr():
        service.okay = False
    refresh_paths(service)
    service.next_cert_changed = True
    return service.okay


def new_cert(service: ServiceData) -> bool:
    """
    Make new certs
     - new always is done in 'next'
    """
    logger = Log()
    logs = logger.logs
    logsv = logger.logsv

    logsv(f'    New cert : {service.svc_name}')

    if not service.state.next.cert_ready:
        logs('    Error: Cert generation not ready - requires csr')
        return False

    lname = 'next'
    db_name = service.db.db_names[lname]
    cert = service.cert[db_name]

    okay = True
    if service.ca_self:
        okay = cert.new_cert_self(service.ca_self)

    elif service.ca_local:
        okay = cert.new_cert_local(service.ca_local)

    elif service.ca_certbot:
        okay = cert.new_cert_certbot(service.ca_certbot)

    if not okay:
        txt = f'{service.grp_name} - {service.svc_name}'
        logs(f'Error creating cert: {txt}')
        return False

    refresh_paths(service)
    service.next_cert_changed = True

    log_cert_expiry(service, lname)

    if not _tlsa_generate_file(service, lname):
        service.okay = False

    return service.okay


def renew_cert(service: ServiceData) -> bool:
    """
    Make new cert if current cert expring, expired or non-existent
    """
    logger = Log()
    logs = logger.logs

    (is_time_to_renew, expires_text) = time_to_renew(service)

    if is_time_to_renew:
        logs(expires_text, opt='mspace')
        logs('    Renewing cert')
        if not new_cert(service):
            service.okay = False
    else:
        logs('    Cert up to date - renew not needed')
    return service.okay


def svc_tlsa_generate(service: ServiceData) -> bool:
    """
    Generate DNS TLSA records for next
    """
    logger = Log()
    logs = logger.logs

    if not service.state.next.tlsa_ready:
        logs('    Error: Not ready to make tlsa - missing cert')
        service.okay = False
        return False

    if not _tlsa_generate_file(service, 'next'):
        service.okay = False
    service.state.update()
    return service.okay


def copy_curr_to_next(service: ServiceData) -> bool:
    """
    Create new next and copy over
    current key and CSR - retain time stamp
    """
    db_name = service.db.db_names['next']
    db_name_curr = service.db.db_names['curr']
    isokay = copy_key_csr(service.db, db_name_curr, db_name)

    ssl_svc = service.svc
    db = service.db
    grp_name = service.grp_name
    service_name = service.svc_name
    opts = service.opts
    service.cert[db_name] = SslCert(db_name, ssl_svc, db,
                                    grp_name, service_name, opts)

    refresh_paths(service)
    return isokay


def roll_next_to_curr(service: ServiceData) -> bool:
    """
    Part of standard roll
    Must be done >= 2xTTL of any DNS tlsa records
     - next must exist
     - check for next being cert/keys being older > min_roll_mins
       wont run without force
    """
    logger = Log()
    logs = logger.logs
    logsv = logger.logsv

    log_space = 'mspace'
    (cert_age, ok_to_roll) = time_to_roll(service)
    if cert_age < 0:
        logsv('    Nothing to roll: no next cert')
        return True     # not an error

    msg = f'cert is {cert_age} mins old'
    if ok_to_roll:
        logs(f'Okay to roll: {msg}', opt='mspace')
    else:
        txt = f'{msg} < {service.opts.min_roll_mins} mins'
        logs(f'Too soon to roll: {txt}', opt=log_space)
        return True         # not an error

    return next_to_curr(service)


def next_to_curr(service: ServiceData) -> bool:
    """
    Make next the new curr
     - for standard options this is 'roll'
     - for dev options its same as roll + force
    """
    logger = Log()
    logger.logsv('    Moving next to curr')

    if not service.db.next_to_curr():
        service.okay = False
    else:
        refresh_paths(service)
        service.curr_cert_changed = True
        service.next_cert_changed = True
    return service.okay


def refresh_paths(service: ServiceData) -> bool:
    """
    After any change to curr/next update to ensure path references up to date
    """
    for (_db_name, cert) in service.cert.items():
        cert.refresh_paths()
    service.state.update()
    return True


def _tlsa_generate_file(service: ServiceData, lname: str) -> bool:
    """
    Wrap call to tlsa_generate_file()
    """
    if not service.dane_tls or not service.ssl_dns:
        return True

    tlsa_item = TlsaItem()

    tlsa_item.apex_domain = service.apex_domain
    tlsa_item.svc_name = service.svc_name
    tlsa_item.lname = lname
    tlsa_item.dane_tls = service.dane_tls
    tlsa_item.db = service.db
    tlsa_item.cert = service.cert
    tlsa_item.ssl_dns = service.ssl_dns

    # tlsa_item.logs = service.logs

    okay = tlsa_generate_file(tlsa_item)
    return okay
