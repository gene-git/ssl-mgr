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

  configs are SslSvc files locatd in:

    <top_dir>/conf.d/<group>/<service>

"""
# pylint: disable=too-many-instance-attributes

import os
from db import get_conf_dir
from .opts_parse import parse_options
from .conf_read import read_ssl_mgr_conf
from .dict_to_opts import dict_to_opts

def _top_dir(conf_dir):
    """
    top_dir has
      conf.d -  has ca-info.conf, directories with domains,  local ca configs
      certs  - has all certs and keys
    """
    top_dir = None
    if conf_dir:
        top_dir = os.path.dirname(conf_dir)
    return top_dir

class SslOpts:
    """
    input for ssl manger
     - command line
    """
    # pylint: disable=too-few-public-methods
    def __init__(self, cmdline:bool=True):
        self.okay = True
        self.conf_dir = get_conf_dir()
        self.top_dir = _top_dir(self.conf_dir)

        # options
        self.verb = False
        self.debug = False
        self.test = False
        self.force = False
        self.reuse_keys = False     # reuse curr/{key,csr}
        self.dry_run = False

        # task command options
        self.status = False
        self.new_csr = False
        self.new_keys = False
        self.new_cert = False
        self.renew_cert = False
        self.refresh_cert = False
        self.renew_cert_now = False
        self.renew_expire_days = 30
        self.renew_expire_days_spread = 0
        self.copy_csr = False
        self.clean_keep = 10
        self.clean_all = False
        self.next_to_curr = False
        self.cert = False
        self.roll = False
        self.min_roll_mins = 90
        self.certs_to_prod = False
        self.dns_refresh = False
        self.root_privs = os.geteuid() == 0

        # config overrides these - may need longer delay
        self.dns_check_delay = 240
        self.dns_xtra_ns = ['1.1.1.1', '8.8.8.8', '9.9.9.9', '208.67.222.222']

        self.post_copy_cmd = None

        # what to do tasks on
        self.grps_svcs = {}

        self.sslm_auth_hook = '/usr/lib/ssl-mgr/sslm-auth-hook'

        self.prod_cert_dir = '/etc/ssl-mgr/prod-certs'
        self.logdir = '/var/log/ssl-mgr'

        conf_dict = read_ssl_mgr_conf(self)
        dict_to_opts(self, conf_dict)

        #
        # Keep copy of config groups/services
        # - needed by tlsa
        self.conf_grps_svcs = self.grps_svcs.copy()

        #
        # Command line opts
        #  - can override ssl-mgr.conf
        #  - parse then map dict to class attributes
        # skipped when called from auth_hook application which has
        # its own command line options
        #
        if cmdline:
            defaults = {'clean_keep' : self.clean_keep,
                        'grps_svcs' : self.grps_svcs,
                        'min_roll_mins' : self.min_roll_mins}
            opt_dict = parse_options(defaults)
            dict_to_opts(self, opt_dict)

        #
        # If test mode - then append ".test" to prod_cert_dir wi
        #
        if self.test:
            self.prod_cert_dir += '.test'

    def __getattr__(self, name):
        """ non-set items simply return None so easy to check existence"""
        return None
