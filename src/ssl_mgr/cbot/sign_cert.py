# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
(Re)New cert from letsencrypt
"""
# pylint: disable=too-many-locals
import os
from utils import run_prog
from utils import read_pem
from config import check_dns_primary
from .acme_register import certbot_acct_check
#from .class_certbot import Certbot

def _domains(csr):
    """
    make comma separated list of domains from sans
    NB the primary domain MUST be the first one listed
    """
    domain_list = csr.svc.x509.sans
    if csr.svc.x509.CN not in domain_list:
        domain_list = [csr.svc.x509.CN] + domain_list

    domains = ','.join(domain_list)
    return domains

def _challenge_type(ca_validation, logs):
    """
    ca_validation has typer and version:  type-vers
    e.g.
        http-01 dns-01
    Extract type.
    """
    if not ca_validation:
        logs(f'Err: Missing ca validation {ca_validation}')
        return None

    challenge_type = None
    if ca_validation.startswith('http'):
        challenge_type = 'http'

    elif ca_validation.startswith('dns'):
        challenge_type = 'dns'

    else:
        logs(f'Err: Bad ca validation {ca_validation}')
    return challenge_type

def certbot_options(certbot:'Certbot', challenge_type:str, cert_dir:str,
                    ssl_ca:"SslCA", ssl_csr:'SslCsr'):
    """
    Construct options to pass to certbot
     - Cerbot puts cert where we tell it to in cert_dir
     - we use apex_domain for cert_name even tho bit redundant in our case
       as we keep each apex_domain in its own dir tree with its own le registered acct
       and thus we do not share multiple apex_domains using same LE acct.
    challenge_type is : "http" or "dns"
    """
    #
    # cb_dir is for certbot to keep account info etc.
    # cert_dir is ours - we ask certbot to put cert and (full)chain there.
    #
    cb_dir = certbot.db.cb_dir

    group = certbot.apex_domain
    #service = certbot.service
    service = ssl_csr.svc.service

    auth_hook = certbot.opts.sslm_auth_hook
    auth_hook_w_args = f'{auth_hook} {group} {service}'

    #
    # No manual cleanup hook needed since we clean up after cert created in
    # certbot.sign_cert() and certbot.renew_cert()
    #
    #cleanup_hook = certbot.opts.sslm_cleanup_hook
    #cleanup_hook_w_args = f'{cleanup_hook} {group} {service}'

    if ssl_ca.debug or certbot.debug:
        auth_hook_w_args = f'{auth_hook_w_args} debug'
    #    cleanup_hook_w_args = f'{cleanup_hook_w_args} debug'

    opts = ['certonly', '--manual']
    opts += ['--quiet', '--keep-until-expiring']
    opts += ['--cert-name', certbot.apex_domain]
    opts += ['--manual-auth-hook', auth_hook_w_args]
    #opts += ['--manual-cleanup-hook', cleanup_hook_w_args]

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

    if certbot.opts.verb:
        opts += ['--debug']

    #
    # Are we testing -
    # - 3 types of testing - can use some or both:
    #
    #   - ssl_ca.test           => from command line : uses LE test/staging server
    #   - ssl_ca.info.ca_test   => conf.d/ca-info.conf : use 'dry-run'
    #   - debug                 => prints instead of running certbot
    #
    # Removing ssl_ca.info.ca_test and using cl opt only now
    #
    if ssl_ca.test :            # or ssl_ca.info.ca_test:
        opts += ['--test-cert']

    if ssl_ca.dry_run:
        opts += ['--dry-run']
    #
    # If not registered with LE then add info to register
    #
    #if not acct_is_reg:
    #    email = ssl_csr.org.x509.email
    #    reg_info = ['--agree-tos', '--no-eff-email', '--email', email]
    #    opts += reg_info


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

def _check_input(certbot, challenge_type):
    """
    Check have whats needed
    """
    opts = certbot.opts
    logs = certbot.logs
    logsv = certbot.logsv

    if challenge_type == 'http':
        if not (opts.web and opts.web.server_dir):
            logs('Error: acme http needs web.server_dir')
            return False

    elif challenge_type == 'dns':
        if not opts.dns :
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

        if not check_dns_primary(logs, opts):
            logs('Error: acme dns needs dns_primary - missing config')
            return False

    return True

def certbot_sign_cert(certbot:'Certbot', ssl_ca:'SslCA',  ssl_csr:'SslCsr'):
    """
    Request a new cert
     - both Certbot Class and here we use link name 'next' to get the right db_name
     - acct is registered is determined by presence of account info files
    """
    logs = certbot.logs
    log = certbot.log

    cb_dir = certbot.db.cb_dir

    db_name = ssl_csr.db_name
    db_dir = certbot.db.db_dir
    cert_dir = os.path.join(db_dir, db_name)

    #
    # sanity check
    #  Should do this in SslCert::check_csr_domain()
    #
    apex_domain = certbot.apex_domain
    logs(f'Sign certbot : {apex_domain}', opt='sdash')
    org_cn = ssl_csr.svc.x509.CN
    if apex_domain != org_cn:
        logs(f'Error: certbot apex domain doesnt match csr: {apex_domain} != {org_cn}')
        return (None, None)
    #
    # Input check
    #
    ca_validation = ssl_ca.info.ca_validation
    challenge_type = _challenge_type(ca_validation, logs)
    if not _check_input(certbot, challenge_type):
        return (None, None)

    #
    # Check account registered, create new account if needed
    #
    account_ok = certbot_acct_check(certbot, ssl_ca, ssl_csr)
    if not account_ok:
        logs(f'  Failed to get acme account {cb_dir}')
        return (None, None)

    #
    # Call certbot to do the work
    #
    opts = certbot_options(certbot, challenge_type, cert_dir, ssl_ca, ssl_csr)

    cmd = ['/usr/bin/certbot']
    pargs = cmd + opts

    log(f'Certbot command: {pargs}')
    if not ssl_ca.debug:
        [_ret, _sout, _serr] = run_prog(pargs, log=logs)

    #
    # Read cert and chain and pass back
    #  - in debug these will return None
    # at this point, all being well, cert_dir has the new
    # cert.pem, chain.pem and fullchain.pem
    #
    if ssl_ca.debug:
        logs('debug on - no cert/chain pem files generated')
        cert_pem = None
        chain_pem = None
    else:
        cert_file = 'cert.pem'
        cert_pem = read_pem(cert_dir, cert_file)

        chain_file = 'chain.pem'
        chain_pem = read_pem(cert_dir, chain_file)

    return (cert_pem, chain_pem)
