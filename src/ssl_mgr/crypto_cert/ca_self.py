# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
  CA class
"""
# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods

from config import (SslOpts, CAInfo)
from ca_sign import (CaSignType, CABase)


class CASelf(CABase):
    """
    For self sign cert. We are our own
    root CA for this case.
    - services (domains/item)
    - signed by local intermediate (sub) CA
    - local sub CA itself is signed by local root CA
    """
    def __init__(self, ca_info: CAInfo, opts: SslOpts):

        ca_sign_type = CaSignType.SELF
        super().__init__(ca_sign_type, ca_info, opts)
