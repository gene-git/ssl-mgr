'''
Convenience class for expirations
'''

from datetime import datetime
from dateutil import tz

class CertExpires:
    '''
    Certificate expiration
     - Time start initialized to now when instantiated.
    '''
    def __init__(self, expiry:datetime):
        '''
        Relative expiration stored as
          expire_days + expire_secs
        '''
        self.expiry = expiry
        self.now = datetime.now(tz.UTC)
        self.expire_days = -1
        self.expire_secs = -1
        self.expire_secs_total = -1

        if not expiry:
            return

        self.init_relative()

    def init_relative(self):
        '''
        Compute expiration relative to now
        '''
        delta = self.expiry - self.now
        self.expire_days = delta.days
        self.expire_secs = delta.seconds
        self.expire_secs_total = self.expire_secs + self.expire_days * 24 * 3600

    def seconds(self) -> int:
        '''
        Expiration in seconds
        '''
        return self.expire_secs_total

    def days(self) -> float:
        '''
        Expiration in days (floating point)
            caller can round, truncate etc
        '''
        return self.expire_days

    def expiration_date_str(self):
        '''
        Expiration as date
        '''
        return str(self.expiry)

    def expiration_string(self):
        '''
        Expiration : xxxd xxh xxm xxs
        '''
        days = int(self.days())
        (hours, seconds) = divmod(self.expire_secs, 3600)
        (minutes, seconds) = divmod(seconds, 60)

        #exp_str = f'{days:>4d}d {hours:>2d}H {minutes:2d}M {seconds:>2d}s'
        exp_str = f'{days:>4d} days + {hours:02d}:{minutes:02d}:{seconds:02d}'
        return exp_str
