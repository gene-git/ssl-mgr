# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  ssl-mgr application command line options
  options:
   - Application works on one or more group-service pairs.
   - Doing multiples, allows a single DNS update which is more efficient.
   - group services pairs are passedon command line:
     group[:service1,service_2,...] group2[:...
    Services are required - special service 'ALL' means all available services will be processed
"""
# pylint: disable=line-too-long,too-many-statements
import sys

def get_available_options(defaults:dict):
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
    opt ~ [ (opt_short, opt_long) { argparse info }]
    opt ~ [ (-x, --xxxx), {'help' : 'help text', 'action' : 'store_true',...  }]

    must have opt_long - opt_short is optional

    NB: options with values must be have default set or will be None
    """

    std_opts = []
    dev_opts = []

    act = 'action'
    act_on = 'store_true'

    ohelp = 'More verbose output'
    opt = [('-v', '--verb'), {'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    ohelp = 'Forces on for renew / roll regardless if too soon'
    opt = [('-f', '--force'), {'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    ohelp = 'Reuse curr key with renew. tlsa unchanged if using selector=1 (pubkey)'
    opt = [('-r', '--reuse'), {'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    ohelp = 'debug mode : print dont do'
    opt =[('-d', '--debug'), {'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    ohelp = 'Letsencrypt --test-cert'
    opt = [('-t', '--test'), {'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    ohelp = 'Letsencrypt --dry-run'
    opt = [('-n', '--dry-run'), {'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    ohelp = 'Display cert status. With --verb shows more info'
    opt = [('-s', '--status'), {'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    ohelp = 'Renew keys/csr/cert keep in next (config renew_expire_days)'
    opt = [('-renew', '--renew'),{'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    ohelp =  'Roll Phase : Make next new curr, copy to production, refresh dns if needed'
    opt = [('-roll', '--roll'), {'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    ohelp = 'Only roll if next is older than this (config min_roll_mins)'
    min_roll_mins = defaults.get('min_roll_mins')
    opt = [('-roll-mins', '--min-roll-mins'), {'help' : ohelp, 'default' : min_roll_mins}]
    std_opts.append(opt)

    ohelp = 'dns: Use script to sign zones & restart primary (config dns.restart_cmd)'
    opt = [('-dns', '--dns-refresh'), {'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    ohelp = 'Clean database dirs keeping newest N (see --clean-all)'
    clean_keep = defaults.get('clean_keep')
    opt = [('-clean-keep', '--clean-keep'), {'help' : ohelp, 'default' : clean_keep}]
    std_opts.append(opt)

    ohelp = 'Clean up all grps/svcs not just active domains'
    opt = [('-clean-all', '--clean-all'), {'help' : ohelp, act : act_on}]
    std_opts.append(opt)

    #
    # Positional Args
    #
    ohelp = 'List groups/services: grp1:[sv1, sv2,...] grp2:[ALL] ...  (default: from config)'
    opt = [('grps_svcs', None), {'help' : ohelp, 'nargs' : '*'}]
    std_opts.append(opt)
    #dev_opts.append(opt)

    #
    # Dev only options (must be separate list)
    #
    dev_opts = std_opts.copy()
    ohelp = 'Make next new keys'
    opt = [('-keys', '--new-keys'), {'help' : ohelp, act : act_on}]
    dev_opts.append(opt)

    ohelp = 'Make next CSR'
    opt = [('-csr', '--new-csr'), {'help' : ohelp, act : act_on}]
    dev_opts.append(opt)

    ohelp = 'Make new next/cert'
    opt = [('-cert', '--new-cert'),{'help' : ohelp, act : act_on}]
    dev_opts.append(opt)

    ohelp = 'Copy curr key to next (used by --reuse)'
    opt = [('-copy', '--copy-csr'), {'help' : ohelp, act : act_on}]
    dev_opts.append(opt)

    ohelp = 'Move next to curr'
    opt = [('-ntoc', '--next-to-curr'), {'help' : ohelp, act : act_on}]
    dev_opts.append(opt)

    ohelp = 'Copy keys/certs : (mail, web, tlsa, etc)'
    opt = [('-certs-prod', '--certs-to-prod'), {'help' : ohelp, act : act_on}]
    dev_opts.append(opt)

    prog = sys.argv[0]
    if len(sys.argv) > 1 and sys.argv[1] == 'dev':
        desc = 'SSL Manager Dev Mode'
        epilog = 'For standard options drop "dev" as 1st argument'
        argv = sys.argv[2:]
        opts = dev_opts
    else:
        desc = 'SSL Manager'
        epilog = 'For dev options add "dev" as 1st argument'
        opts = std_opts
        argv = sys.argv[1:]

    return (prog, desc, epilog, argv, opts)
