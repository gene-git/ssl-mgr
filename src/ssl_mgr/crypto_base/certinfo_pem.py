# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Given pem string with one or more components  return list of cert_info
for each component
"""
from .certinfo_utils import (key_pem_info, csr_pem_info, cert_pem_info)
from .certinfo import (CertInfo)


def _extract_label(line: str) -> tuple[str, str]:
    """
    Takes: -----BEGIN [LABEL]-----
    Returns (BEGIN, LABEL) or
    or (None, None)
    """
    line_split = line.split('-----')
    if len(line_split) != 3:
        return ('', '')

    key = ''
    label = ''
    key_label = line_split[1]
    (key, label) = key_label.split(' ', 1)

    return (key, label)


def cert_split_pem_string(pemstring: str) -> list[tuple[str, str]]:
    """
    Certificate pem files are often concatenated.
    chain.pem for example contains multiple certs.
    Separate the components and return cert info for each
    Each item can be cert, key or csr
    We mark the "type" based on header:
    -----BEGIN [LABEL]-----
    ... data
    -----END [LABEL]-----
    [LABEL] can be :
        PRIVATE KEY, CERTIFICATE, CERTIFICATE REQUEST,

    Input: string with 1 or more PEM components
    Output: list of (label, pem)
    where label is one of the RFC 7468 labels
    NB:
    For openssl trusted certificates there is ExtraData after the cert -
      which has the trust data.
      cryptography.x509 will not load this
      see : https://github.com/pyca/cryptography/issues/5242
    """
    pem_items: list[tuple[str, str]] = []
    if not pemstring:
        return pem_items

    pem_lines = pemstring.splitlines()
    for line in pem_lines:
        if line.startswith('#') or line.strip().startswith('\n'):
            continue

        (key, label) = _extract_label(line)

        if key == 'BEGIN':
            this_data = line + '\n'
            this_label = label

        elif key == 'END':
            this_data += line + '\n'
            this_item = (this_label, this_data)
            pem_items.append(this_item)
            this_data = ''

        else:
            this_data += line + '\n'

    return pem_items


def cert_info_from_pem_string(pemstring: str) -> list[CertInfo]:
    """
    Certificate pem files are often concatenated.
    chain.pem for example contains multiple certs.
    Separate the components and return cert info for each
    Each item can be cert, key or csr
    We mark the "type" based on header:
    -----BEGIN xxx-----
    xxx can be :
        PRIVATE KEY, CERTIFICATE, CERTIFICATE REQUEST, PUBLIC KEY,

    We currently do not handle:
        X509 CRL, PKCS7, CMS, ENCRYPTED PRIVATE KEY, ATTRIBUTE CERTIFICATE
    """
    cert_infos: list[CertInfo] = []

    pem_items = cert_split_pem_string(pemstring)
    if not pem_items:
        return cert_infos

    for (label, pem) in pem_items:

        pem_bytes = pem.encode()
        if 'KEY' in label:
            info = key_pem_info(pem_bytes)

        elif 'REQUEST' in label:
            info = csr_pem_info(pem_bytes)

        elif 'CERTIFICATE' in label:
            info = cert_pem_info(pem_bytes)

        else:
            # unsupported = try cert
            info = cert_pem_info(pem_bytes)

        cert_infos.append(info)
    return cert_infos
