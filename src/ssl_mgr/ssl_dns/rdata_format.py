# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Formats TXT records
See https://datatracker.ietf.org/doc/html/rfc6698
"""
from textwrap import wrap

def dns_tlsa_record_format(tlsa_key, tlsa_val, indent:int=20):
    """
    Format TLSA rdata records.
    Input: 
        tlsa_key and tlsa_val strings
    tlsa_key = usage selector match type
        e.g. tlsa_key = "3 1 1"
    tlsa_val is hex digest string.
    DNS Max of one string is 255, 
    which is split at 72 for readability
    e.g. output rdata: 
        name IN TXT rdata:
    rdata <tlsa_key> <value>
        tlsa_key tlsa_val
            or
        ( tlsa_key
          tlsa_val_1
          tlsa_val_2 ... )
    TLSA records dont need to be quoted (it seems)
    """
    max_one = 72
    if len(tlsa_val) < max_one:
        rdata = f'{tlsa_key} {tlsa_val}'
        return rdata

    val_split = wrap(tlsa_val, max_one)
    rdata = f'( {tlsa_key}'
    ind = indent * ' '
    for string in val_split:
        rdata += f'\n{ind}{string}'            # Add double quotes around string?
    rdata += ' )'
    return rdata

def dns_txt_record_format(txt_val, indent:int=20):
    """
    Format TXT records.
    Input :
        unquoted string
    Max of any one string is 255, split 
    split at 72 for readability
    Output rdata :
        "rdata"
            or
        ( "rdata-1"
          "rdata-2"
          "rdata-3" ... )
    Since we split at 60 we dont use the format:
       "string-1" "string-2'
    """
    max_one = 72
    if len(txt_val) < max_one:
        rdata = f'"{txt_val}"'
        return rdata

    val_split = wrap(txt_val, max_one)
    rdata = '('
    ind = indent * ' '
    for string in val_split:
        rdata += f'\n{ind}"{string}"'
    rdata += ' )'
    return rdata
