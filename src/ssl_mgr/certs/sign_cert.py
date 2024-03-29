#!/usr/bin/python
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Crypto primative - certs
Called from ssl_ca.sign_cert()
"""
# pylint: disable=too-many-locals
from cbot import Certbot
from .class_csr import SslCsr
from .self_sign_cert import own_sign_cert

def sign_cert(ssl_ca:'SslCA', db_dir:str, ssl_csr:SslCsr):
    """
    Give csr to appropriate CA to get a signed cert
    """
    if ssl_ca.info.ca_type == 'self':
        #
        # Signed by our own self signed CA
        #
        (cert_pem, chain_pem) = own_sign_cert(db_dir, ssl_ca, ssl_csr)

    elif ssl_ca.info.ca_type == 'certbot':
        #
        # Signed by letencrypt (via Certbot)
        #
        #apex_domain = ssl_csr.csr.get_subject().CN
        apex_domain = ssl_csr.svc.group
        service = ssl_csr.svc.service
        deb = False
        if ssl_ca.debug:
            deb = True

        certbot = Certbot('next', apex_domain, service, debug=deb)
        (cert_pem, chain_pem) = certbot.sign_cert(db_dir, ssl_ca, ssl_csr)

    else:
        ssl_ca.logs(f'Error: CA type {ssl_ca.ca_info.type} not supported')
        cert_pem = None
        chain_pem = None

    return (cert_pem, chain_pem)
