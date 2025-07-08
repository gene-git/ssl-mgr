# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
File logger class
Provides to separate logging facilities:
 one for certbot and one for non-certbot tools.

Each offers log to file, log to stdout and verbose/non-verbose
capabilities. They also provide for additional tags
such as leading spaces,  dashes and warn/info/error.
"""
# pylint: disable=missing-function-docstring
# pylint: disable=global-statement
import os
from enum import Enum

import logging
from logging.handlers import RotatingFileHandler
from .file_tools import make_dir_path


# --------------------------------
#     PRIVATE INTERNAL
#
def _opt_tag(msg: str, opt: str) -> tuple[str, str]:
    '''
    log additional tag
      can be above or in front of message
    '''
    # pylint: disable=too-many-branches
    above = ''
    front = ''
    if opt:
        if opt == 'dash':
            above = len(msg) * '-'

        elif opt == 'sdash':
            above = 4 * '-'

        elif opt == 'mdash':
            above = 16 * '-'

        elif opt == 'ldash':
            above = 24 * '-'

        elif opt == 'warn':
            front = 4 * '-' + ' Warn ' + 4 * '-'

        elif opt == 'error':
            front = 4 * '-' + ' Error ' + 3 * '-'

        elif opt == 'info':
            front = 4 * '-' + ' Info ' + 3 * '-'

        elif opt == 'space':
            front = 4 * ' '

        elif opt == 'sspace':
            front = 8 * ' '

        elif opt == 'mspace':
            front = 12 * ' '

        elif opt == 'lspace':
            front = 16 * ' '

        elif opt == 'xlspace':
            front = 32 * ' '

        elif opt.startswith('space-'):
            optsplit = opt.split('-')
            if len(optsplit) > 1:
                num_spaces = int(optsplit[1])
                front = num_spaces * ' '

    return (above, front)


def _opt_tags(msg: str, opt: str | list[str] | None = None) -> tuple[str, str]:
    '''
    Process any optional tags
    '''
    if not opt:
        return ('', '')

    opts = opt
    if isinstance(opt, str):
        opts = [opt]

    above = ''
    front = ''
    for one in opts:
        (this_above, this_front) = _opt_tag(msg, one)
        if this_above:
            above += this_above
        if this_front:
            front += this_front
    return (above, front)


class _SslLog:
    """
    Our little logger tool
     - on instance per named log
    """
    def __init__(self, logdir: str, name: str):
        self.log_path = os.path.join(logdir, name)
        self.verb = False

        # make sure logdir exists
        if not os.path.isdir(logdir) and not make_dir_path(logdir):
            print(f'Error creating log dir {logdir}')

        # format
        log_fmt = '%(asctime)s %(message)s'
        dt_fmt = '%Y-%m-%d %H:%M:%S '
        formatter = logging.Formatter(fmt=log_fmt, datefmt=dt_fmt)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        handler = RotatingFileHandler(self.log_path,
                                      maxBytes=204800, backupCount=4)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def set_verb(self, verb: bool):
        """
        set verbose flag state
        """
        self.verb = verb

    def log(self, msg: str, opt: str | list[str] | None = None):
        """
        Write msg to:
         - log file
        """
        (above, front) = _opt_tags(msg, opt)
        if above:
            self.logger.info(above)
        self.logger.info(front + msg)

    def logs(self, msg: str, opt: str | list[str] | None = None):
        """
        write msg to
         - log file
         - stdout
        """
        (above, front) = _opt_tags(msg, opt)
        if above:
            self.logger.info(above)
            print(above)
        self.logger.info(front + msg)
        print(front + msg)

    def logv(self, msg: str, opt: str | list[str] | None = None):
        """
        write to
         - log file but only if verb is true
        """
        if self.verb:
            (above, front) = _opt_tags(msg, opt)
            if above:
                self.logger.info(above)
            self.logger.info(front + msg)

    def logsv(self, msg: str, opt: str | list[str] | None = None):
        """
        Write msg to
         - log file
         - stdout only if verb is true
        """
        (above, front) = _opt_tags(msg, opt)
        if above:
            self.logger.info(above)
            if self.verb:
                print(above)

        self.logger.info(front + msg)
        if self.verb:
            print(front + msg)

    def logfile(self):
        """
        Return log file path.
        """
        return self.log_path


# --------------------------------
#     PUBLIC
#
class LogZone(Enum):
    """
    Way to request which log file is written.
    Better than passing around functions.
    """
    GENERAL = 0
    CERTBOT = 1


class Log:
    """
    Handle all logging
    """
    _zone: LogZone = LogZone.GENERAL
    _general: _SslLog
    _certbot: _SslLog
    _log: _SslLog
    _initialized: bool = False

    @staticmethod
    def initialize(logdir: str, zone: LogZone = LogZone.GENERAL):
        if not Log._initialized:
            Log._general = _SslLog(logdir, 'sslm')
            Log._certbot = _SslLog(logdir, 'cbot')
            Log._initialized = True
            Log.set_zone(zone)

    @staticmethod
    def set_zone(zone: LogZone):
        Log._zone = zone
        if Log._zone == LogZone.CERTBOT:
            Log._log = Log._certbot
        else:
            Log._log = Log._general

    @staticmethod
    def is_initialized():
        return Log._initialized

    @staticmethod
    def log(msg: str, opt: str | list[str] | None = None):
        if Log._initialized:
            Log._log.log(msg, opt)

    @staticmethod
    def logs(msg: str, opt: str | list[str] | None = None):
        if Log._initialized:
            Log._log.logs(msg, opt)

    @staticmethod
    def logv(msg: str, opt: str | list[str] | None = None):
        if Log._initialized:
            Log._log.logv(msg, opt)

    @staticmethod
    def logsv(msg: str, opt: str | list[str] | None = None):
        if Log._initialized:
            Log._log.logsv(msg, opt)

    @staticmethod
    def set_verb(verb: bool):
        if Log._initialized:
            Log._log.set_verb(verb)
