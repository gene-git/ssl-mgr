# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
    toml file tools
    needs python >= 3.11
"""
from typing import (Any)
import os
import tomllib as toml
import tomli_w
from .read_write import open_file


def _dict_remove_none(dic: dict[str, Any]) -> dict[str, Any]:
    """
    Rmoves keys with None values
    returns copy of dictionary
    """
    clean: dict[str, Any] = {}
    if not dic:
        return clean

    for key, val in dic.items():
        if val is not None:
            if isinstance(val, dict):
                new_val = _dict_remove_none(val)
                if new_val:
                    clean[key] = new_val
            else:
                clean[key] = val
    return clean


def dict_to_toml_string(dic: dict[str, Any]) -> str:
    """
    Returns a toml formatted string from a dictionary
      - Keys with None values are removed/ignored
    """
    clean_dict = _dict_remove_none(dic)
    txt = tomli_w.dumps(clean_dict)
    return txt


def read_toml_file(fpath: str) -> dict[str, Any]:
    """
    read toml file and return a dictionary
    """
    this_dict: dict[str, Any] = {}
    if os.path.exists(fpath):
        fobj = open_file(fpath, 'r')
        if fobj:
            data = fobj.read()
            fobj.close()
            this_dict = toml.loads(data)
    return this_dict


def write_toml_file(dic: dict[str, Any], fpath: str) -> bool:
    """
    read toml file and return a dictionary
    """
    okay = True
    if not dic or not fpath:
        return okay

    txt = dict_to_toml_string(dic)
    if txt:
        fobj = open_file(fpath, 'w')
        if fobj:
            fobj.write(txt)
            fobj.close()
        else:
            okay = False
    return okay
