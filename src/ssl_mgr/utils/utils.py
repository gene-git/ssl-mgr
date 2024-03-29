# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Misc utils
"""
#import os
import socket
from datetime import datetime

def current_date_time_str(fmt='%Y%m%d-%H:%M:%S'):
    """
    date time string
    """
    today = datetime.today()
    today_str = today.strftime(fmt)
    return today_str

def get_my_hostname():
    """ return (hostname, fqdn) """
    fqdn = socket.gethostname()
    host = fqdn.split('.')[0]
    return (host, fqdn)

def get_domain():
    """ return domain name of current host """
    fqdn = socket.gethostname()
    dsplit = fqdn.split('.')
    dsplit = dsplit[-2:]
    domain = '.'.join(dsplit)
    return domain
