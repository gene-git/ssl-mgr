# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  service level tasks
"""
import time

def time_to_renew(service):
    """
    Check if time to renew
    renew when:
     - no cert
     - days to expiration < ssl_svc.renew_expire_days
    """
    #
    # Have cert - check if ready or too new to renew/refresh
    #
    log_space = 'mspace'
    renew = True
    db_name = service.db.db_names['curr']
    if db_name:
        (expiry_date_str, days_left) = service.cert[db_name].cert_expiration()
        days_to_renew = days_left - service.svc.renew_expire_days
        msg = f'↪ Current cert expires: {expiry_date_str} ({days_left} days)'
        if days_to_renew > 0 :
            #service.logs(f'    {msg} -> Renew in {days_to_renew}')
            service.logs(f'{msg} 🗘 Renew in {days_to_renew}', opt=log_space)
            renew = False
        else:
            #service.logs(f'    {msg} -> Renew now')
            service.logs(f'{msg} 🗘 Renew now', opt=log_space)
    else:
        service.logs(' Warning - no curr certs (first cert or missed roll?) - generating new next')

    return renew

def log_cert_expiry(service, lname):
    """ log curr/cert expiry """
    log_space = 'mspace'
    db_name = service.db.db_names[lname]
    (expiry_date_str, days_left) = service.cert[db_name].cert_expiration()
    service.logs(f'↪ Renewed cert expires: {expiry_date_str} ({days_left} days)', opt=log_space)

def _age_in_mins(age_secs):
    """ convert secs to mins secs """
    secs = round(age_secs, 0)
    mins = max(int(secs / 60), 1)
    return mins

def time_to_roll(service):
    """
    Check if next/cert is at least min_roll_mins old
    return true if time to roll
    """

    #
    # Next must exist
    #
    if not service.state.next.cert_time:
        # no next - nothing to roll
        return (-1, False)

    #
    # Check next cert age
    #
    secs_to_nano = 1000000000
    min_roll_time = service.opts.min_roll_mins * 60 * secs_to_nano

    next_cert_age = time.time_ns() - service.state.next.cert_time

    age_mins = _age_in_mins(next_cert_age / secs_to_nano)

    #
    # ok if next/cert old enough for DNS to get out.
    # Or no curr - also okay to roll
    #
    if next_cert_age >= min_roll_time or not service.state.curr.cert_time:
        return (age_mins, True)

    return (age_mins, False)
