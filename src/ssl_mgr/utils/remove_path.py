# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
 file utils
"""
import os
import shutil

from .class_log import Log


def remove_path(path: str) -> bool:
    """
    Remove file or directory and its contents.
    """
    logger = Log()
    logs = logger.logs

    if not path or not os.path.exists(path):
        return True

    #
    # Handle not a directory
    #
    if os.path.islink(path) or os.path.isfile(path):
        try:
            os.unlink(path)
        except OSError as exc:
            logs(f' Error removing {path}: {exc}')
            return False
        return True

    #
    # not file or dir - bail
    #
    if not os.path.isdir(path):
        logs(f' Error removing {path} - unkown file type.')
        return False

    #
    # Directory
    #
    try:
        shutil.rmtree(path)
    except OSError as exc:
        logs(f' Error removing {path} : {exc}.')
        return False
    return True
