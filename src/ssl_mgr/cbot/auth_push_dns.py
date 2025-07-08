# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
auth push for dns-01
"""
# pylint: disable=too-many-locals
import os
import time

from utils import open_file
from utils import (Log)
from dns_base import (init_primary_dns_server,  dns_zone_update, dns_restart)
from dns_base import (dns_txt_record_format)

from .certbothook_data import CertbotHookData


def _acme_challenges(apex_domain: str, auth_data_rows: list[str]):
    """
     - create the acme challenge dns TXT records
     - create list of (domain, validation) items from auth_data
       Used to check all NS have the validation info

     - each auth_data row contains:
       domain validation_strng

    returns: (dns_rr_str, challenges)
    dns_rr_str = All dns txt records as string with newlines
    challenges  = List of (domain, validation) pairs :
                 [(domain, validation), ... ]
    """
    rr_ttl = '60'
    dns_rr = f';; acme-challenge : {apex_domain}\n'

    challenges = []
    for row in auth_data_rows:
        if row == '' or row.startswith('#') or row.startswith(';'):
            continue

        (domain, validation) = row.split()
        if domain.startswith('*.'):
            #
            # wildcards validate using apex_domain
            # which require their own (duplicate) apex_domain row
            # e.g. *.example.com => example.com
            #
            domain = domain[2:]
        #
        # challenge validation strings are usually < 255 chars
        # so shouldn't need to split them into smaller strings.
        # However, we call dns txt formatter to be safe.
        # Also, note that formatter adds quotes around the string.
        #
        rdata = dns_txt_record_format(validation)
        dns_row = f'_acme-challenge.{domain}. {rr_ttl} IN TXT {rdata}\n'

        dns_rr += dns_row
        challenges.append((f'{domain}', f'{validation}'))

    return (dns_rr, challenges)


def _save_dns_acme_file(cb_dir: str, apex_domain: str, dns_rr: str) -> str:
    """
    Save the file with acme challenges TXT records
      <cb_dir>/acme-challenge.<apex_domain>
    Returns : path to saved dns file
    """
    dns_file = f'acme-challenge.{apex_domain}'
    dns_path = os.path.join(cb_dir, dns_file)
    fobj = open_file(dns_path, 'w')
    if fobj:
        fobj.write(f';; acme-challenge for : {apex_domain}\n')
        fobj.write(dns_rr)
        fobj.close()
        return dns_path
    return ''


def auth_push_dns(certbot: CertbotHookData,
                  auth_data_rows: list[str],
                  check_nameservers: bool = True):
    """
    Send acme-challenges to dns so letsencrypt can validate.
    Create DNS acme-challenge TXT records in single file.
    Send file to dns server - which we then have zones
    signed and primary dns restarted.
    Each row of input is one acme-challenge
    Save each validation string into file of all dns TXT RR
      each row : domain validation
    Used only for dns:
     - acme-challenge validation
    """
    #
    # Dont need logger.set_zone(LogZone.CERTBOT)
    # As should be already set at the top
    #
    logger = Log()
    logs = logger.logs

    logs('    auth_push_dns', opt='sdash')

    apex_domain = certbot.apex_domain
    cb_dir = certbot.db.cb_dir
    deb = False
    if certbot.debug:
        deb = certbot.debug

    #
    # Get
    #  - dns_rr : string of DNS TXT records for all challenges
    #  - challenges : [(domain, validation), ...]
    #    pairs to confirm dns NS servers have them
    #
    (dns_rr, challenges) = _acme_challenges(apex_domain, auth_data_rows)

    #
    # Save:
    #  TXT records to file : <cb_dir/acme-challenge.<apex-domain>
    #
    dns_path = _save_dns_acme_file(cb_dir, apex_domain, dns_rr)

    #
    # Copy acme challenge file (dns_path) to dns acme directory / directories
    # This has all challenges for the current cert.
    # dns_acme_dir has one or more directories
    #
    dns_acme_dir = certbot.opts.dns.acme_dir
    isokay = dns_zone_update(dns_path, dns_acme_dir, debug=deb)
    if not isokay:
        logs('Error with dns_zone_update (see log file)')

    #
    # DNS update = (sign zone and restart primary)
    # auth-hook will be called by certbot to check that all
    #
    domains: list[str] = [apex_domain]
    isokay = dns_restart(domains, certbot.opts, debug=deb)
    if not isokay:
        logs('Error with dns_restart (see log file)')

    #
    # Cleanup doesn't need any nameserver checks
    # It just wants to push empty acme-challenge TXT records to the zone
    #
    if not check_nameservers:
        logs('    auth_push_dns - skipping nameserver checks')
        return

    #
    # Wait and only return after all auth nameservers have
    # the correct acme validation challenges
    # Certbot will check with the authorized NS to validate challenge
    #
    # - sanity check primary NS has correct acme challenges
    #   if not we have major problem.
    # - get serial of primary NS
    # - check each ns has current serial
    #
    dns = init_primary_dns_server(certbot.opts, apex_domain)
    if deb:
        subdoms = [sub for (sub, _val) in challenges]
        logs(f'Debug skip: dns acme check {apex_domain} : {subdoms}')
        return

    ns_updated = dns.check_acme_challenges(challenges)
    if not ns_updated:
        hail_mary = 600
        txt = f'hail mary delay {hail_mary}'
        logs(f'Failed to validate all nameservers: {txt}')
        time.sleep(hail_mary)
        ns_updated = dns.check_acme_challenges(challenges)
        if not ns_updated:
            logs('  Still Failed to validate all nameservers.  Fatal error')
