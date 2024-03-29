# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Check class_svc has needed info
"""
from typing import Callable

def _check_x509(svc:"SslSvc", log:Callable[[str], None]) -> bool:
    """
    X509 is required
    """
    is_okay = True

    if not svc.x509:
        log(' Svc : missing X509 Section')
        is_okay = False
    else:
        if not svc.x509.CN:
            log(' Svc : missing CN')
            is_okay = False

        if not svc.x509.O:
            log(' Svc : missing O')
            is_okay = False

        if not svc.x509.C:
            log(' Svc : missing C')
            is_okay = False

        if not svc.ca:
            if not svc.x509.sans:
                log(' Svc : Must have at least CN in sans list')
                is_okay = False

            elif svc.x509.CN not in svc.x509.sans:
                log(' Svc : san_list must have CN')
                is_okay = False
    return is_okay

def _check_keyopts(svc:"SslSvc", log:Callable[[str], None]) -> bool:
    """
    KeyOpts is required
    """
    is_okay = True
    if svc.keyopts:
        if not svc.keyopts.ktype:
            log(' Svc : missing KeyOpts.ktype (rsa, ec)')
            is_okay = False
    else:
        log(' Svc : missing KeyOpts Section')
        is_okay = False

    return is_okay

def _check_ca(svc:"SslSvc", log:Callable[[str], None]) -> bool:
    """
    CA section only relevant for self-signed root or sub
    """
    is_okay = True
    if svc.ca:
        if not svc.ca.sign_end_days:
            log(' Svc : CA missing sign_end_days')
            is_okay = False

        if not svc.ca.digest:
            log(' Svc : CA missing sigest')
            is_okay = False
    return is_okay

def check_svc(svc:"SslSvc", log:Callable[[str], None]) -> bool:
    """
    Validate needed info is present
    """
    is_okay = True
    if not svc.name:
        log(' Svc : missing name')
        is_okay = False

    if not _check_x509(svc, log) :
        is_okay = False

    if not _check_keyopts(svc, log) :
        is_okay = False

    if not _check_ca(svc, log) :
        is_okay = False

    return is_okay
