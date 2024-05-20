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
    """ log additional tag """
    tag = None
    if opt :
        if opt == 'dash':
            tag = len(msg) * '-'

        elif opt == 'sdash':
            tag = 4 * '-'

        elif opt == 'mdash':
            tag = 16 * '-'

        elif opt == 'ldash':
            tag = '\n' + 24 * '-'

        elif opt == 'warn':
            tag = 4 * '-' + ' Warn ' + 4 * '-'

        elif opt == 'error':
            tag = 4 * '-' + ' Error ' + 3 * '-'

        elif opt == 'info':
            tag = 4 * '-' + ' Info ' + 3 * '-'

    return tag

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

    def log(self, msg:str, opt:str=None):
        """
        write this to log
        """
        tag = _opt_tag(msg, opt)
        if tag:
            self.logger.info(tag)
        self.logger.info(msg)

    def logs(self, msg:str, opt:str=None):
        """
        write msg to
         - log 
         - stdout
        """
        tag = _opt_tag(msg, opt)
        if tag:
            self.logger.info(tag)
            print(tag)
        self.logger.info(msg)
        print(msg)

    def logv(self, msg:str, opt:str=None):
        """
        write to 
         - log if verb is true
        """
        if self.verb:
            tag = _opt_tag(msg, opt)
            if tag:
                self.logger.info(tag)
            self.logger.info(msg)

    def logsv(self, msg:str, opt:str=None):
        """
        write msg to 
         - log 
         - stdout when verb is true
        """
        tag = _opt_tag(msg, opt)
        if tag:
            self.logger.info(tag)
            if self.verb:
                print(tag)

        self.logger.info(msg)
        if self.verb:
            print(msg)

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
