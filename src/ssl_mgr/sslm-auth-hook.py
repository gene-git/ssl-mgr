#!/usr/bin/python
# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
 dns-01/http-01 Authentication script for certbot letsencrypt
 Set via the certbot option: --manual-auth-hook /path/to/me
 This script gets called repeatedly for each domain/SAN.
 When CERTBOT_REMAINING_CHALLENGES == 0 then all (sub)domains on this cert
 are done - for http we dont wait, but for dns we batcj up all the 
 validations and update dns once.

 Script gets 2 arguments passed in : group service
 We use these to locate the correct working directory

 env variables passed down:
     Env :
        $CERTBOT_DOMAIN     = the domain being authenticated
        $CERTBOT_VALIDATION = validation string (for HTTP-01 DNS-01)
        $CERTBOT_TOKEN      = resource filename requested if HTTP-01 challenge
        $CERTBOT_REMAINING_CHALLENGES = number of challenges that remain after the current one,
        $CERTBOT_ALL_DOMAINS    =  a comma-separated list of all domains that are
                                    challenged for the current certificate

        Needs to know if challenge files are on local machine or remote machine
        set the webserver variable at top of file - or better we add a config file to read

  Config files:
    <conf_dir>/ (see db/conf.py)
               certbot.conf
               <group>/<service>

    These provide info needed to use http-01 and dns-01 validation
    Info includes server names and, if needed, how to restart web server and push dns out
"""
# pylint: disable=invalid-name
# pylint: disable=R0801
import os
import sys
from cbot import CertbotHook

def _group_service():
    """
     args must be passed in : group service [debug]
    """
    prog = sys.argv[0]
    prog = os.path.basename(prog)
    (group, service, debug) = (None, None, False)

    if len(sys.argv) < 3:
        return (prog, group, service, debug)

    group = sys.argv[1]
    service = sys.argv[2]
    if len(sys.argv) > 3 and sys.argv[3].lower().startswith('deb'):
        debug = True
    return (prog, group, service, debug)

def main():
    """
    Certificate manager
     - does http / dns based on application name
       cb-auth-http or cb-auth-dns
    """
    #breakpoint()

    (_prog, group, service, deb ) = _group_service()
    certbot = CertbotHook('next', group, service, opts=None, debug=deb)

    certbot.auth_hook()

if __name__ == '__main__':
    main()
