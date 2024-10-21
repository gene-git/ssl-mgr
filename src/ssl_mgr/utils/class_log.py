# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: © 2023-present  Gene C <arch@sapience.com>
"""
File logger class
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from .file_tools import make_dir_path

def _opt_tag(msg, opt:str):
    '''
    log additional tag
      can be above or in front of message
    '''
    # pylint: disable=too-many-branches
    above = ''
    front = ''
    if opt :
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

def _opt_tags(msg, opt:str|list[str]|None=None) -> str:
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

class SslLog:
    """
    Our little logger tool
     - on instance per named log
    """
    def __init__(self, logdir, name):
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

        handler = RotatingFileHandler(self.log_path, maxBytes=102400, backupCount=1)
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def set_verb(self, verb:bool):
        """ set verbose flag """
        self.verb = verb

    def log(self, msg:str, opt:str|list[str]|None=None):
        """
        write this to log
        """
        (above,front) = _opt_tags(msg, opt)
        if above:
            self.logger.info(above)
        self.logger.info(front + msg)

    def logs(self, msg:str, opt:str|list[str]|None=None):
        """
        write msg to
         - log
         - stdout
        """
        (above,front) = _opt_tags(msg, opt)
        if above:
            self.logger.info(above)
            print(above)
        self.logger.info(front + msg)
        print(front + msg)

    def logv(self, msg:str, opt:str|list[str]|None=None):
        """
        write to
         - log if verb is true
        """
        if self.verb:
            (above,front) = _opt_tags(msg, opt)
            if above:
                self.logger.info(above)
            self.logger.info(front + msg)

    def logsv(self, msg:str, opt:str|list[str]|None=None):
        """
        write msg to
         - log
         - stdout when verb is true
        """
        (above,front) = _opt_tags(msg, opt)
        if above:
            self.logger.info(above)
            if self.verb:
                print(above)

        self.logger.info(front + msg)
        if self.verb:
            print(front + msg)

    def logfile(self):
        """ where to find log """
        return self.log_path

# --------- GLOBAL LOGGERS -------------------
MGR_LOGGER = None
CERTBOT_LOGGER = None

def init_logging(logdir):
    """
    Set up logging facility
    Logging
     - mgr_logger  : logs for ssl-mgr et al
     - cbot_logger : logs for by certbot
    """
    # pylint: disable=global-statement
    mgr_logger = SslLog(logdir, 'sslm')
    cbot_logger = SslLog(logdir, 'cbot')

    global MGR_LOGGER
    MGR_LOGGER = mgr_logger

    global CERTBOT_LOGGER
    CERTBOT_LOGGER = cbot_logger

def get_logger():
    """ logger for ssl-mgr """
    return MGR_LOGGER

def get_certbot_logger():
    """ logger for certbot programs """
    return CERTBOT_LOGGER
