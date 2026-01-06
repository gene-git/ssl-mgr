# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Check class_svc has needed info
"""
from ssl_mgr.utils import Log

from .service_conf_data import ServiceConfData


def _check_x509(svc: ServiceConfData) -> bool:
    """
    X509 is required
    """
    is_okay = True
    logger = Log()
    logs = logger.logs

    if not svc.x509:
        logs(' Svc: missing X509 Section')
        is_okay = False
    else:
        if not svc.x509.CN:
            logs(' Svc: missing CN')
            is_okay = False

        if not svc.x509.O:
            logs(' Svc: missing O')
            is_okay = False

        if not svc.x509.C:
            logs(' Svc: missing C')
            is_okay = False

        if not svc.ca:
            if not svc.x509.sans:
                logs(' Svc: Must have at least CN in sans list')
                is_okay = False

            elif svc.x509.CN not in svc.x509.sans:
                logs(' Svc: san_list must have CN')
                is_okay = False
    return is_okay


def _check_keyopts(svc: ServiceConfData) -> bool:
    """
    KeyOpts is required
    """
    logger = Log()
    logs = logger.logs

    is_okay = True
    if svc.keyopts:
        if not svc.keyopts.ktype:
            logs(' Svc: missing KeyOpts.ktype (rsa, ec)')
            is_okay = False
    else:
        logs(' Svc: missing KeyOpts Section')
        is_okay = False

    return is_okay


def _check_ca(svc: ServiceConfData) -> bool:
    """
    CA section only relevant for self-signed root or sub
    """
    logger = Log()
    logs = logger.logs
    is_okay = True
    if svc.ca:
        if not svc.ca.sign_end_days:
            logs(' Svc: CA missing sign_end_days')
            is_okay = False

        if not svc.ca.digest:
            logs(' Svc: CA missing digest')
            is_okay = False
    return is_okay


def check_svc(svc: ServiceConfData) -> bool:
    """
    Validate needed info is present
    """
    logger = Log()
    logs = logger.logs
    is_okay = True
    if not svc.name:
        logs(' Svc: missing name')
        is_okay = False

    if not _check_x509(svc):
        is_okay = False

    if not _check_keyopts(svc):
        is_okay = False

    return is_okay
