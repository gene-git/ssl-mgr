# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  service level tasks
"""
# pylint: disable=invalid-name

def cert_status(svc:'Service'):
    """
    Display cert status
    Add info about production cert? Has to be at app level not here
    """
    logs = svc.logs

    space = 8 * ' '

    for lname in ['curr', 'next']:
        db_name = svc.db.db_names[lname]
        if db_name and svc.cert[db_name]:
            cert_info = svc.cert[db_name].cert_info()

            if not cert_info:
                logs(f'{space} {lname:<12s} : Failed to read cert')
                continue

            expiry_date_str = cert_info.expiry_date_str
            #days_left = cert_info.days_left
            expiry_string = cert_info.expiry_string

            #expire_info = f'expires: {expiry_date_str} ({days_left} days)'
            expire_info = f'expires: {expiry_date_str} ({expiry_string})'
            logs(f'{space} {lname:<12s} : {expire_info}')
            logs(f'{space} {"issuer":>12s} : CN={cert_info.issuer_CN} O={cert_info.issuer_O}')
            logs(f'{space} {"subject":>12s} : CN={cert_info.subject_CN}')
            logs(f'{space} {"pubkey":>12s} : {cert_info.pubkey_info}')

            if svc.opts.verb:
                logs(f'{space} {"sans":>12s} : {cert_info.sans}')
                logs(f'{space} {"sig_algo":>12s} : {cert_info.sig_algo}')
    return True
