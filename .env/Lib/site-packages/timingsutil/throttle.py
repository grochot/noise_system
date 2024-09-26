# encoding: utf-8

import logging
from .timeout import Timeout


class Throttle(object):

    def __init__(self,
                 rate=None,
                 interval=None):

        """
        Perpetually restarting timer
        Example use is to limit the number of requests per second to a service

        :param rate: allowed events per second
        :param interval: time in seconds before next event is permitted
        """

        if rate:
            try:
                self.interval = 1.0 / rate

            except ZeroDivisionError:
                self.interval = 0

        else:
            self.interval = interval

        # logging.debug(u'Throttle interval:{interval}'
        #               .format(interval=interval))

        self.timeout = Timeout(seconds=self.interval)

    def wait(self,
             message=None):
        self.timeout.wait(message=message)
        self.timeout.restart()
