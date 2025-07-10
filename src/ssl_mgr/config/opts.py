# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
ssl-mgr application command line options
options:
 - Application works on one or more group-service pairs.
 - Doing multiples, allows a single DNS update which is more efficient.
 - group services pairs are passedon command line:
   group[:service1,service_2,...] group2[:...
   Services are required - special service 'ALL' means
   all available services will be processed
"""
# pylint: disable=line-too-long, too-many-statements
import sys

type Opt = tuple[str | tuple[str, str], dict[str, str]]


def get_available_options(defaults: dict[str, str]):
    """
    List of command line options for argparse
    2 kinds of options
     * standard
       Normal production use: renew, roll-2, status, ...)
     * dev
       development mode adds access to all options
       such as new-keys, new-csr, new-cert etc.

    Returns list of options: [opt1, opt2, ...]

    Each opt is to be used with argparse:

    NB: options with values must be have default set or will be None
    """

    std_opts: list[Opt] = []
    dev_opts: list[Opt] = []

    ohelp = 'Clean up all grps/svcs not just active domains'
    std_opts.append((('-clean-all', '--clean-all'),
                     {'help': ohelp,
                      'action': 'store_true'}
                     ))

    std_opts.append((('-d', '--debug'),
                     {'help': 'debug mode : print but dont do it',
                      'action': 'store_true'}
                     ))

    ohelp = 'dns: Use script to sign zones & restart primary'
    ohelp += '\nSee config dns.restart_cmd'
    std_opts.append((('-dns', '--dns-refresh'),
                     {'help': ohelp,
                      'action': 'store_true'}
                     ))

    std_opts.append((('-f', '--force'),
                     {'help': 'Forces renew / roll / prod check',
                      'action': 'store_true'}
                     ))

    ohelp = 'Letsencrypt --dry-run'
    std_opts.append((('-n', '--dry-run'),
                     {'help': 'Letsencrypt --dry-run',
                      'action': 'store_true'}
                     ))

    ohelp = 'Reuse curr key with renew.'
    ohelp += 'tlsa unchanged if using selector=1 (pubkey)'
    std_opts.append((('-r', '--reuse'),
                     {'help': ohelp,
                      'action': 'store_true'}
                     ))

    ohelp = 'Renew keys/csr/cert keep in next (config renew_expire_days)'
    std_opts.append((('-renew', '--renew'),
                     {'help': ohelp,
                      'action': 'store_true'}
                     ))

    ohelp = 'Roll Phase : Make next the new curr and copy to production'
    ohelp += '\nRefresh dns if needed'
    std_opts.append((('-roll', '--roll'),
                     {'help': ohelp,
                      'action': 'store_true'}
                     ))

    min_roll_mins = '90'
    if isinstance(defaults.get('min_roll_mins'), int):
        min_roll_mins = str(defaults.get('min_roll_mins'))

    ohelp = 'Only roll if next is older than this (config min_roll_mins)'
    std_opts.append((('-roll-mins', '--min-roll-mins'),
                     {'help': ohelp,
                      'default': min_roll_mins}
                     ))

    ohelp = 'Display cert status. With --verb shows more info'
    std_opts.append((('-s', '--status'),
                     {'help': ohelp,
                      'action': 'store_true'}
                     ))

    std_opts.append((('-t', '--test'),
                     {'help': 'Letsencrypt --test-cert',
                      'action': 'store_true'}
                     ))

    ohelp = 'Clean database dirs keeping newest N (see --clean-all)'
    clean_keep = '5'
    if isinstance(defaults.get('clean_keep'), int):
        clean_keep = str(defaults.get('clean_keep'))

    std_opts.append((('-clean-keep', '--clean-keep'),
                     {'help': ohelp,
                      'default': clean_keep}
                     ))

    std_opts.append((('-v', '--verb'),
                     {'help': 'More verbose output',
                      'action': 'store_true'}
                     ))

    #
    # Positional Args
    #
    ohelp = 'List groups/services: grp1:[sv1, sv2,...] grp2:[ALL] ... '
    ohelp += 'Default is taken from config'
    std_opts.append((('grps_svcs'),
                     {'help': ohelp,
                      'nargs': '*'}
                     ))

    #
    # Dev only options (must be separate list)
    #
    dev_opts = std_opts.copy()
    dev_opts.append((('-cert', '--new-cert'),
                     {'help': 'Make new next/cert',
                      'action': 'store_true'}
                     ))

    dev_opts.append((('-csr', '--new-csr'),
                     {'help': 'Make next CSR',
                      'action': 'store_true'}
                     ))

    dev_opts.append((('-copy', '--copy-csr'),
                     {'help': 'Copy curr key to next (used by --reuse)',
                      'action': 'store_true'}
                     ))

    ohelp = 'Forces server restarts even if not needed'
    dev_opts.append((('-fsr', '--force-server-restarts'),
                     {'help': ohelp,
                      'action': 'store_true'}
                     ))

    dev_opts.append((('-keys', '--new-keys'),
                     {'help': 'Make next new keys',
                      'action': 'store_true'}
                     ))

    dev_opts.append((('-ntoc', '--next-to-curr'),
                     {'help': 'Move next to curr',
                      'action': 'store_true'}
                     ))

    dev_opts.append((('-certs-prod', '--certs-to-prod'),
                     {'help': 'Copy keys/certs : (mail, web, tlsa, etc)',
                      'action': 'store_true'}
                     ))

    std_opts.sort(key=lambda item: item[0][0].lower())
    dev_opts.sort(key=lambda item: item[0][0].lower())

    prog = sys.argv[0]
    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        desc = 'SSL Manager Dev Mode'
        epilog = 'For standard options drop "dev" as 1st argument'
        argv = sys.argv[2:]
        opts = dev_opts
    else:
        desc = 'SSL Manager'
        epilog = 'For dev options add "dev" as 1st argument'
        argv = sys.argv[1:]
        opts = std_opts

    return (prog, desc, epilog, argv, opts)
