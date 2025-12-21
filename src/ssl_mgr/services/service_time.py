# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
service level tasks
"""
# pylint: disable=too-many-locals
# import time
import random

from utils import Log

from ._service_data import ServiceData


def _get_rand_adjust_days(spread: int | None) -> tuple[int, int]:
    '''
    If using renew_expire_days_spread > 0 then
    Generate and return random integer in range:
        [-spread, spread]
    Return
        (spread, adjustment)
        returned spread is set to 0 if input is negative
    '''
    if not spread or spread <= 0:
        return (0, 0)

    adjust = random.randrange(-spread, spread + 1)
    return (spread, adjust)


def _renew_in_text(spread: float, days_to_renew: float) -> str:
    '''
    message for next renewal
    '''
    when = f'{days_to_renew:.1f}'
    if spread > 0:
        if days_to_renew > 0:
            when += f' ± {spread:.1f}'
        else:
            when = f'0 ± {spread:.1f}'
    return when


def time_to_renew(service: ServiceData,
                  lname: str = 'curr') -> tuple[bool, str]:
    """
    Check if time to renew
    renew when:
     - no cert
     - days to expiration < ssl_svc.renew_expire_days
    Returns:
        (istime, expiration_string)
    """
    #
    # If renew_expire_days_spread > 0 then get a random number
    # of days between -spread and + spread
    #
    renew_info = service.opts.renew_info

    # older code.
    # renew_expire_days = service.svc.renew_expire_days
    # renew_expire_days_spread = service.svc.renew_expire_days_spread
    # (spread, renew_adjust) = _get_rand_adjust_days(renew_expire_days_spread)

    #
    # Have cert - check if ready or too new to renew/refresh
    #
    renew_now = True
    cert_expires = None

    db_name = service.db.db_names[lname]
    if db_name:
        cert_expires = service.cert[db_name].cert_expires()

    if cert_expires:
        expiry_date_str = cert_expires.expiration_date_str()
        expiry_str = cert_expires.expiration_string()
        days_left = cert_expires.days()
        # issue_days = cert_expires.issue_days()
        lifetime = cert_expires.lifetime_at_issue()

        # days_to_renew = int(days_left - renew_expire_days)
        (renew_now, days_to_renew, spread) = renew_info.renew_decision(lifetime, days_left)

        txt = f'{expiry_date_str} ({expiry_str})'
        exp_curr_str = f'↪ Current cert expires: {txt}'

        if renew_now:
            exp_curr_str += ' 🗘 Renew now'
        else:
            renew_in = _renew_in_text(spread, days_to_renew)
            exp_curr_str += f' 🗘 Renew in {renew_in} days'

        # if days_to_renew > -renew_adjust:
        #    renew_now = False
        #    renew_in = _renew_in_text(spread, days_to_renew)
        #    exp_curr_str += f' 🗘 Renew in {renew_in} days'
        # else:
        #    exp_curr_str += ' 🗘 Renew now'
    else:
        exp_curr_str = 'No curr certs (first cert or missed roll?): '
        exp_curr_str += 'generating new cert'

    return (renew_now, exp_curr_str)


def log_cert_expiry(service: ServiceData, lname: str):
    """
    log curr/cert expiry
    """
    logger = Log()
    logs = logger.logs

    log_space = 'mspace'
    db_name = service.db.db_names[lname]

    cert_expires = service.cert[db_name].cert_expires()
    if cert_expires:
        # check in case of failure
        expiry_date_str = cert_expires.expiration_date_str()
        expiry_str = cert_expires.expiration_string()
    else:
        expiry_date_str = 'not found'
        expiry_str = 'missing cert?'

    # logs(f'  {service.svc_name}')
    txt = f'{expiry_date_str} ({expiry_str})'
    logs(f'↪ Renewed cert expires: {txt}', opt=log_space)


def get_expiration_text(service: ServiceData, lname: str) -> str:
    '''
    Standard expiration string
    '''
    (_is_time_to_renew, expiration_str) = time_to_renew(service, lname)

    return expiration_str


def _age_in_mins(age_secs: float) -> int:
    """
    convert secs to mins secs
    """
    secs = round(age_secs, 0)
    mins = max(int(secs / 60), 1)
    return mins


def time_to_roll(service: ServiceData) -> tuple[int, bool]:
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

    db_name = service.db.db_names['next']
    if not db_name:
        return (-1, False)

    #
    # Check next cert age
    # - use issue date in cert (not_before X509 date)
    # secs_to_nano = 1000000000
    # min_roll_time = service.opts.min_roll_mins * 60 * secs_to_nano
    # next_cert_age = time.time_ns() - service.state.next.cert_time
    # age_mins = _age_in_mins(next_cert_age / secs_to_nano)

    min_roll_secs = float(service.opts.min_roll_mins * 60)
    cert_expires = service.cert[db_name].cert_expires()
    if not cert_expires:
        return (-1, False)

    age_secs = cert_expires.issued_secs
    age_mins = _age_in_mins(age_secs)

    #
    # ok if next/cert old enough for DNS to get out.
    # Or no curr - also okay to roll
    #
    # if next_cert_age >= min_roll_time or not service.state.curr.cert_time:
    if age_secs >= min_roll_secs or not service.state.curr.cert_time:
        return (age_mins, True)

    return (age_mins, False)
