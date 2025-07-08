# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
(Re)New cert from letsencrypt
"""
# pylint: disable=too-many-locals
import os

from utils import run_prog
from utils import read_pem
from utils import Log

from config import check_dns_primary
from crypto_csr import (SslCsr)
from ca_sign import (CACertbot)

from .acme_register import certbot_acct_check
from .certbothook_data import CertbotHookData


def _domains(csr: SslCsr):
    """
    make comma separated list of domains from sans
    NB the primary domain MUST be the first one listed
    """
    domain_list = csr.svc.x509.sans
    if csr.svc.x509.CN not in domain_list:
        domain_list = [csr.svc.x509.CN] + domain_list

    domains = ','.join(domain_list)
    return domains


def _challenge_type(ca_validation: str) -> str:
    """
    ca_validation has typer and version:  type-vers
    e.g.
        http-01 dns-01
    Extract type.
    """
    logger = Log()
    logs = logger.logs

    if not ca_validation:
        logs(f'Err: Missing ca validation {ca_validation}')
        return ''

    challenge_type = ''
    if ca_validation.startswith('http'):
        challenge_type = 'http'

    elif ca_validation.startswith('dns'):
        challenge_type = 'dns'

    else:
        logs(f'Err: Bad ca validation {ca_validation}')
    return challenge_type


def certbot_options(certbot: CertbotHookData,
                    challenge_type: str,
                    cert_dir: str,
                    ca_certbot: CACertbot,
                    ssl_csr: SslCsr):
    """
    Construct options to pass to certbot
     - Cerbot puts cert where we tell it to in cert_dir
     - we use apex_domain for cert_name even tho bit redundant in our case
       as we keep each apex_domain in its own dir tree with
       its own le registered acct and thus we do not share multiple
       apex_domains using same LE acct.
    challenge_type is : "http" or "dns"
    """
    #
    # cb_dir is for certbot to keep account info etc.
    # cert_dir is ours - we ask certbot to put cert and (full)chain there.
    #
    cb_dir = certbot.db.cb_dir

    group = certbot.apex_domain
    service = ssl_csr.svc.service

    auth_hook = certbot.opts.sslm_auth_hook
    auth_hook_w_args = f'{auth_hook} {group} {service}'

    #
    # No manual cleanup hook needed since we clean up after cert created in
    # certbot.sign_cert() and certbot.renew_cert()
    #
    if ca_certbot.debug or certbot.debug:
        auth_hook_w_args = f'{auth_hook_w_args} debug'
    #    cleanup_hook_w_args = f'{cleanup_hook_w_args} debug'

    opts = ['certonly', '--manual']
    opts += ['--logs-dir', certbot.logdir_letsencrypt]
    opts += ['--work-dir', certbot.workdir_letsencrypt]
    opts += ['--quiet', '--keep-until-expiring']
    opts += ['--cert-name', certbot.apex_domain]
    opts += ['--manual-auth-hook', auth_hook_w_args]
    # opts += ['--manual-cleanup-hook', cleanup_hook_w_args]

    #
    # Where to save all the certs and chains
    #
    cert_path = os.path.join(cert_dir, 'cert.pem')
    key_path = os.path.join(cert_dir, 'key.pem')
    chain_path = os.path.join(cert_dir, 'chain.pem')
    fullchain_path = os.path.join(cert_dir, 'fullchain.pem')

    opts += ['--cert-path', cert_path]
    opts += ['--key-path', key_path]
    opts += ['--chain-path', chain_path]
    opts += ['--fullchain-path', fullchain_path]

    #
    # LE defaults to 'ISRG Root X1' (RSA).
    # can also use ca_preferred_chain = 'ISRG Root X2' (ECC)
    #
    if ca_certbot.ca_info.ca_preferred_chain:
        opts += ['--preferred-chain', ca_certbot.ca_info.ca_preferred_chain]

    #
    # Are we testing -
    # - 3 types of testing - can use some or both:
    #
    # - ca_certbot.test => from command line : uses LE test/staging server
    # - ca_certbot.info.ca_test => conf.d/ca-info.conf : use 'dry-run'
    # - debug               => prints instead of running certbot
    #
    # Removing ca_certbot.info.ca_test and using cl opt only now
    #
    if certbot.opts.verb:
        opts += ['--debug']

    if certbot.opts.test:
        opts += ['--test-cert']

    if ca_certbot.dry_run:
        opts += ['--dry-run']
    #
    # If not registered with LE then add info to register
    # - no longer needed/used

    #
    # All domains in this cert.
    #
    domains = _domains(ssl_csr)

    csr_path = os.path.join(cert_dir, ssl_csr.file)

    #
    # dont need key type as we use our own and public key is in csr.
    #
    opts += ['--config-dir', cb_dir]
    opts += ['--domains', domains]
    opts += ['--csr', csr_path]
    opts += [f'--preferred-challenges={challenge_type}']

    return opts


def _check_input(certbot: CertbotHookData, challenge_type: str) -> bool:
    """
    Check have whats needed
    """
    logger = Log()
    logs = logger.logs
    logsv = logger.logsv
    opts = certbot.opts

    if challenge_type == 'http':
        if not (opts.web and opts.web.server_dir):
            logs('Error: acme http needs web.server_dir')
            return False

    elif challenge_type == 'dns':
        if not opts.dns:
            logs('Error: acme dns needs dns - no dns in config')
            return False

        if not opts.dns.acme_dir:
            logs('Error: acme dns needs dns acme_dir')
            return False

        if not opts.dns.restart_cmd:
            logs('Error: acme dns needs dns restart_cmd')
            return False

        if not opts.dns.tlsa_dirs:
            logsv('Warning: acme dns tlsa needs tlsa_dirs')

        if not check_dns_primary(opts):
            logs('Error: acme dns needs dns_primary - missing config')
            return False

    return True


def certbot_sign_cert(certbot: CertbotHookData,
                      ca_certbot: CACertbot,
                      ssl_csr: SslCsr
                      ) -> tuple[bytes, bytes]:
    """
    Request a new cert
     - both Certbot Class and here we sym link name 'next'
       to get the right db_name
     - acct is registered is determined by presence of account info files
    """
    logger = Log()
    logs = logger.logs
    log = logger.log

    cb_dir = certbot.db.cb_dir

    db_name = ssl_csr.db_name
    db_dir = certbot.db.db_dir
    cert_dir = os.path.join(db_dir, db_name)

    #
    # sanity check
    #  Should do this in SslCert::check_csr_domain()
    #
    apex_domain = certbot.apex_domain
    logs(f'    Sign certbot : {apex_domain}', opt='sdash')
    org_cn = ssl_csr.svc.x509.CN
    if apex_domain != org_cn:
        txt = f'{apex_domain} != {org_cn}'
        logs(f'Error: certbot apex domain doesnt match csr: {txt}')
        return (b'', b'')
    #
    # Input check
    #
    ca_validation = ca_certbot.ca_info.ca_validation
    challenge_type = _challenge_type(ca_validation)
    if not _check_input(certbot, challenge_type):
        return (b'', b'')

    #
    # Check account registered, create new account if needed
    #
    account_ok = certbot_acct_check(certbot, ca_certbot, ssl_csr)
    if not account_ok:
        logs(f'  Failed to get acme account {cb_dir}')
        return (b'', b'')

    #
    # Call certbot to do the work
    #
    pargs = ['/usr/bin/certbot']
    cmd_opts = certbot_options(certbot, challenge_type,
                               cert_dir, ca_certbot, ssl_csr)
    pargs += cmd_opts

    log(f'Certbot command: {pargs}')
    if not ca_certbot.debug:
        (_ret, _sout, _serr) = run_prog(pargs)

    #
    # Read cert and chain and pass back
    #  - in debug these will return None
    # at this point, all being well, cert_dir has the new
    # cert.pem, chain.pem and fullchain.pem
    #
    if ca_certbot.debug:
        logs('debug on - no cert/chain pem files generated')
        cert_pem = b''
        chain_pem = b''
    else:
        cert_file = 'cert.pem'
        cert_pem = read_pem(cert_dir, cert_file)

        chain_file = 'chain.pem'
        chain_pem = read_pem(cert_dir, chain_file)

    return (cert_pem, chain_pem)
