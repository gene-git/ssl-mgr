# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Read the ca-info.conf file
"""
import os
from utils import read_toml_file

def _read_ca_info_conf(top_dir:str):
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
    """
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.ca_desc = ''
        self.ca_type = None
        self.ca_validation = None

    def init_ca_name(self, top_dir:str, ca_name:str):
        """
        Read all available ca-infos and 
        find ca_name to initialize self
        """

        # read all available
        ca_info_dic = _read_ca_info_conf(top_dir)

        # find ca_name
        info_dict = ca_info_dic.get(ca_name)

        if not info_dict:
            return False

        # set our attributes
        for (key, val) in info_dict.items():
            setattr(self, key, val)
        return True
