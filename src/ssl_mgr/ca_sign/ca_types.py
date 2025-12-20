# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
  CA class
"""
from enum import Enum


class CaSignType(Enum):
    """ supported cert authority types """
    UNKNOWN = 0
    SELF = 1
    LOCAL = 2
    CERTBOT = 3
