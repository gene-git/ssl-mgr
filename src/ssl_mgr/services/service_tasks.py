# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  service level tasks
"""
# pylint: disable=invalid-name
from certs import SslCert
from tlsa import tlsa_generate
from .copy_key_csr import copy_key_csr
from .service_time import time_to_renew, log_cert_expiry, time_to_roll

def check_next_cert_changed(service):
    """
    determine if next cert changed
    - at start no next and have next -> changed
    - time next/cert > time of cert at start 
    - instead of time should we retrieve the fingerprint?
    """
    if service.next_cert_changed:
        return service.next_cert_changed

    if not service.next_cert_time :
        if service.state.next.cert_time:
            service.next_cert_changed = True

    elif service.state.next.cert_time :
        if service.state.next.cert_time > service.next_cert_time:
            service.next_cert_changed = True

    return service.next_cert_changed

def check_curr_cert_changed(service):
    """
    determine if curr cert changed if:
      - at start no curr and have curr 
      - time curr/cert != time of cert at start (should we enforce newer)
    - instead of time should we retrieve the fingerprint?
    """
    if service.curr_cert_changed:
        return service.curr_cert_changed

    if not service.curr_cert_time :
        if service.state.curr.cert_time:
            service.curr_cert_changed = True

    elif service.state.curr.cert_time :
        if service.state.curr.cert_time > service.curr_cert_time:
            service.curr_cert_changed = True

    return service.curr_cert_changed

def new_next(service):
    """
    Make new 'next' dir
    """
    if not service.db.new_next():
        service.okay = False
    refresh_paths(service)
    return service.okay

def new_key_pair(service):
    """
    Make new key pairs
    - new always for 'next'
    """
    db_name = service.db.db_names['next']
    if not db_name:
        service.logs('    Error: cant make new keys next dir is missing')
        return False

    ssl_svc = service.svc
    db = service.db
    grp_name = service.grp_name
    service_name = service.svc_name
    opts = service.opts

    service.cert[db_name] = SslCert(db_name, ssl_svc, db, grp_name, service_name, opts)

    refresh_paths(service)
    if not service.state.next.privkey_ready:
        service.logs('    Error: Not ready to make privkey - unclear why')
        service.okay = False
        return False

    if not service.cert[db_name].new_key_pair():
        service.okay = False
        return False

    refresh_paths(service)
    return True

def new_csr(service):
    """
    Make new key pairs
     - new always for 'next'
     - since keys must come first, cert[db_name] must existo
     - should we confirmn?
    """
    if not service.state.next.csr_ready:
        service.logs('    Error: Make csr requires keys')
        service.okay = False
        return False

    lname = 'next'
    db_name = service.db.db_names[lname]
    if not service.cert[db_name].new_csr():
        service.okay = False
    refresh_paths(service)
    return service.okay

def new_cert(service):
    """
    Make new certs
     - new always is done in 'next'
    """
    service.logsv(f'    New cert : {service.svc_name}')

    if not service.state.next.cert_ready:
        service.logs('    Error: Cert generation not ready - requires csr')
        return False

    lname = 'next'
    db_name = service.db.db_names[lname]
    if not service.cert[db_name].new_cert(service.ca):
        service.okay = False
    refresh_paths(service)

    log_cert_expiry(service, lname)
    if not tlsa_generate(service, lname):
        service.okay = False

    return service.okay

def renew_cert(service):
    """
    Make new cert if current cert expring, expired or non-existent
    """
    renew = time_to_renew(service)

    if renew:
        service.logs('    Renewing cert')
        if not new_cert(service):
            service.okay = False
    else:
        service.logs('    Cert up to date - renew not needed')
    return service.okay

def svc_tlsa_generate(service):
    """
    Generate DNS TLSA records for next
    """
    if not service.state.next.tlsa_ready:
        service.logs('    Error: Not ready to make tlsa - missing cert')
        service.okay = False
        return False

    if not tlsa_generate(service, 'next'):
        service.okay = False
    service.state.update()
    return service.okay

def copy_curr_to_next(service):
    """
    Create new next and copy over
    current key and CSR - retain time stamp
    """
    db_name = service.db.db_names['next']
    db_name_curr = service.db.db_names['curr']
    isokay = copy_key_csr(service.db, db_name_curr, db_name, service.logs)

    ssl_svc = service.svc
    db = service.db
    grp_name = service.grp_name
    service_name = service.svc_name
    opts = service.opts
    service.cert[db_name] = SslCert(db_name, ssl_svc, db, grp_name, service_name, opts)

    refresh_paths(service)
    return isokay

def roll_next_to_curr(service):
    """
    Part of standard roll
    Must be done >= 2xTTL of any DNS tlsa records
     - next must exist
     - check for next being cert/keys being older > min_roll_mins
       wont run without force
    """
    log_space = 'mspace'
    (cert_age, ok_to_roll) = time_to_roll(service)
    if cert_age < 0:
        service.logsv('    Nothing to roll: no next cert')
        return True     # not an error

    msg = f'cert is {cert_age} mins old'
    if ok_to_roll:
        service.logs(f'Okay to roll: {msg}', opt=log_space)
    else:
        service.logs(f'Too soon to roll: {msg} < {service.opts.min_roll_mins} mins', opt=log_space)
        return True         # not an error

    return next_to_curr(service)

def next_to_curr(service):
    """
    Make next the new curr
     - for standard options this is 'roll'
     - for dev options its same as roll + force
    """
    service.logsv('    Moving next to curr')
    if not service.db.next_to_curr():
        service.okay = False
    else:
        refresh_paths(service)
        service.cert_changed = True
    return service.okay

def refresh_paths(service):
    """
    After any change to curr/next update to ensure path references up to date
    """
    for (_db_name, cert) in service.cert.items():
        cert.refresh_paths()
    service.state.update()
