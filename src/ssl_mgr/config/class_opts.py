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

configs are ServiceConf files locatd in:
  <top_dir>/conf.d/<group>/<service>

"""
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from .opts_parse import parse_options
from .conf_read import read_ssl_mgr_conf
from .dict_to_opts import dict_to_opts
from ._opts_data import SslOptsData


class SslOpts(SslOptsData):
    """
    input for ssl manger
     - command line
    """
    def __init__(self, called_from_certbot: bool = False):
        #
        # If certbot hook, which has its
        # separate command line options we
        # skip some things.
        # called_from_hook = True (was cmdline = False)
        # and vice versa
        #
        self.called_from_certbot: bool = called_from_certbot
        super().__init__()

        conf_dict = read_ssl_mgr_conf(self)
        dict_to_opts(self, conf_dict)

        #
        # Keep copy of config groups/services
        # - needed by tlsa
        #
        self.conf_grps_svcs = self.grps_svcs.copy()

        #
        # Command line opts
        #  - can override ssl-mgr.conf
        #  - parse then map dict to class attributes
        # skipped when called from auth_hook application which has
        # its own command line options and sets cmdline = False
        #
        if not called_from_certbot:
            defaults = {'clean_keep': self.clean_keep,
                        'grps_svcs': self.grps_svcs,
                        'min_roll_mins': self.min_roll_mins}
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
