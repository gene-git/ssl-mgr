# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
Read the ca-info.conf file
"""
# pylint: disable=too-few-public-methods
import os
from ssl_mgr.utils import read_toml_file


def _read_ca_info_conf(top_dir: str):
    """
    Read the conf.d/ca-info.conf
    Return dictionary of CAInfo
      { 'name_1' : ca_info1, 'name_2' : ca_info2,.... }
    """
    file = 'ca-info.conf'
    cainfo_path = os.path.join(top_dir, 'conf.d', file)

    ca_info_dic = read_toml_file(cainfo_path)
    if not ca_info_dic:
        print(f'Failed to read {file}')
        return None

    return ca_info_dic


class CAInfo():
    """
    Simple container with one CA info read from ca-info.conf file

    Would be more efficient to read file once and then pull
    each ca_info by name from that file. This is simpler.
    """
    # pylint: disable=too-few-public-methods
    def __init__(self):
        """
        Should we limit preferred_acme_profile='tlsserver' for
        ca_type = 'certbot'
        """
        self.ca_name: str = ''
        self.ca_desc: str = ''
        self.ca_type: str = ''
        self.ca_validation: str = ''
        self.ca_preferred_chain: str = ''       # Not needed any longer with LE Gen Y root
        self.ca_preferred_acme_profile: str = 'tlsserver'


class CAInfos:
    """
    Holds what is know about all certificate authorities.
    """
    def __init__(self, top_dir: str):

        # indexed by ca_name
        self.ca_infos: dict[str, CAInfo] = {}

        # read all available
        ca_info_dic = _read_ca_info_conf(top_dir)
        if not ca_info_dic:
            return

        for (ca_name, one_dict) in ca_info_dic.items():
            info = CAInfo()
            info.ca_name = ca_name
            for (key, val) in one_dict.items():
                setattr(info, key, val)
            self.ca_infos[ca_name] = info

    def get_info(self, ca_name: str) -> CAInfo | None:
        """
        Return the CAInfo by name.

        If not found None is returned.
        """
        if ca_name in self.ca_infos:
            return self.ca_infos[ca_name]
        return None
