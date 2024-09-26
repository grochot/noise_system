# encoding: utf-8

import logging
import datetime
from past.builtins import basestring


class TimeIncrementer(object):

    DEFAULT_PERIOD = 300

    def __init__(self,
                 start=None,
                 period=DEFAULT_PERIOD,
                 fmt=None):
        u"""
        Returns times based periods above the start time.
        Use next() to advance the 'current' by the period.

        :param start:  datetime object or None
        :param period: timedelta object or a time in seconds
        :param fmt:    A strftime time format string. e.g. "%H:%M"
                       If this is ommitted, datetimes are returned.

        """
        if start is None:
            start = datetime.datetime.now()
        elif isinstance(start, basestring):
            try:
                start = datetime.datetime.strptime(start, fmt)
            except (ValueError, TypeError) as ve:
                logging.exception(ve)
                raise ValueError(u'Start value ("{start}") cannot be converted to {format}'
                                 .format(start=start,
                                         format=fmt))
        self._start = (datetime.datetime.now()
                       if start is None
                       else start)
        self._current = self._start
        try:
            self._period = (period
                            if isinstance(period, datetime.timedelta)
                            else datetime.timedelta(seconds=period))
        except Exception as e:
            logging.exception(e)
            raise ValueError(u'Period value ("{period}") cannot be converted to datetime.timedelta'
                             .format(period=period))
        self._fmt = fmt

    def formatted(self,
                  value):
        if self._fmt:
            return value.strftime(self._fmt)
        else:
            return value

    @property
    def start(self):
        return self.formatted(self._start)

    @property
    def current(self):
        return self.formatted(self._current)

    def next(self):
        self._current += self._period
        return self.current
