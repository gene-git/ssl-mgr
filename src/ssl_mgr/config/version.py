# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
Project ssl-mgr
"""
__version__ = "6.3.0"
__date__ = "2025-09-08"
__reldev__ = "release"


def version() -> str:
    """ report version and release date """
    vers = f'ssl-mgr: version {__version__} ({__reldev__}, {__date__})'
    return vers
