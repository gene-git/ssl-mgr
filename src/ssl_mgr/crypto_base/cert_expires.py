# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
'''
Convenience class for expirations
'''
# pylint: disable=too-many-instance-attributes
from datetime import datetime
from dateutil import tz


class CertExpires:
    '''
    Certificate expiration
     - Time start initialized to now when instantiated.
    '''
    def __init__(self, not_valid_before_utc: datetime, not_valid_after_utc: datetime):
        '''
        Relative expiration stored as
          expire_days + expire_secs
        '''
        self.now: datetime = datetime.now(tz.UTC)

        # expiration (x509: not_valid_after_utc)
        # relative is postive = expiry - now
        self.expiry: datetime = not_valid_after_utc
        self.expire_days: int = -1
        self.expire_secs: int = -1
        self.expire_secs_total: int = -1

        #
        # issued (x509: not_valid_before_utc)
        # relative is positive value = now - issue
        #
        self.issued: datetime = not_valid_before_utc
        self.issued_days: int = -1
        self.issued_secs: int = -1
        self.issued_secs_total: int = -1

        # expiration length (relative to when issued)
        self.expire_days_at_issue: int = -1
        self.expire_secs_at_issue: int = -1
        self.expire_secs_total_at_issue: int = -1

        if not not_valid_after_utc:
            return

        self.init_relative()

    def init_relative(self):
        '''
        Compute expiration relative to now
        '''
        # expiration
        delta = self.expiry - self.now
        self.expire_days = delta.days
        self.expire_secs = delta.seconds
        # self.expire_secs_total = delta.seconds + delta.days * 24 * 3600
        self.expire_secs_total = int(delta.total_seconds())

        # issued
        delta = self.now - self.issued
        self.issued_days = delta.days
        self.issued_secs = delta.seconds
        # self.issued_secs_total = delta.seconds + delta.days * 24 * 3600
        self.issued_secs_total = int(delta.total_seconds())

        # expiration at issue
        delta = self.expiry - self.issued
        self.expire_days_at_issue = delta.days
        self.expire_secs_at_issue = delta.seconds
        # self.expire_secs_total_at_issue = delta.seconds + delta.days * 24 * 3600
        self.expire_secs_total_at_issue = int(delta.total_seconds())

    def seconds(self) -> int:
        '''
        Expiration in seconds
        '''
        return self.expire_secs_total

    def issue_seconds(self) -> int:
        """
        seconds since issue
        """
        return self.issued_secs_total

    def days(self) -> float:
        '''
        Expiration in days (floating point)
            caller can round, truncate etc
        '''
        days = float(self.expire_secs_total) / (24*3600)
        return days

    def issue_days(self) -> float:
        """
        Days since issue
        """
        days = float(self.issued_secs_total) / (24*3600)
        return days

    def lifetime_at_issue(self) -> float:
        """
        Original lifetime at issue
        """
        days = float(self.expire_secs_total_at_issue) / (24*3600)
        return days

    def expiration_date_str(self):
        '''
        Expiration as date
        '''
        return str(self.expiry)

    def issue_date_str(self):
        '''
        Expiration as date
        '''
        return str(self.issued)

    def expiration_string(self):
        '''
        Expiration : xxxd xxh xxm xxs
        '''
        days = int(self.days())
        (hours, seconds) = divmod(self.expire_secs, 3600)
        (minutes, seconds) = divmod(seconds, 60)

        # exp_str = f'{days:>4d}d {hours:>2d}H {minutes:2d}M {seconds:>2d}s'
        exp_str = f'{days:>4d} days + {hours:02d}:{minutes:02d}:{seconds:02d}'
        return exp_str

    def issue_string(self):
        '''
        Issued : xxxd xxh xxm xxs
        issue time is issue - now (which is negative)
        '''
        days = int(self.issue_days())
        (hours, seconds) = divmod(self.issued_secs, 3600)
        (minutes, seconds) = divmod(seconds, 60)

        orig_days = round(self.expire_secs_total_at_issue/3600 / 24)
        orig_info = f'ago. {orig_days} day cert'

        # do we add "ago" at the end?
        issue_str = f'{days:>4d} days + {hours:02d}:{minutes:02d}:{seconds:02d} {orig_info}'
        return issue_str
