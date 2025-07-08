# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Verify cert
"""
from cryptography import x509
from cryptography.exceptions import InvalidSignature

from crypto_base import read_cert


def cert_verify(cert: x509.Certificate,
                chain: x509.Certificate) -> tuple[bool, str]:
    """
    verify cert using chain's public key
    Input  : x509 Certificates: cert, chain
    Output : (verify_status, message)
    """
    verified = False
    try:
        cert.verify_directly_issued_by(chain)
        verified = True
        msg = 'Cert verified'

    except ValueError:
        msg = 'Cert bad: issuer name doesnt match issuer subject in chain'
        msg += '\n       or signature algorithm is unsupported'

    except TypeError:
        msg = 'Cert bad: issuer doesnt have supported public key type'

    except InvalidSignature:
        msg = 'Cert bad: signature fails to verify'

    return (verified, msg)


def cert_verify_file(cert_path: str, chain_path: str) -> tuple[bool, str]:
    """
    Given cert and chain pem files
    Verify the cert
    """
    cert = read_cert(cert_path)
    chain = read_cert(chain_path)

    if not (cert and chain):
        msg = 'Failed to read cert or chain file'
        return (False, msg)

    (verified, msg) = cert_verify(cert, chain)
    return (verified, msg)
