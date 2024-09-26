# encoding: utf-8

import logging
from .timeout import TimersBase


class Stopwatch(TimersBase):

    def __init__(self,
                 high_precision=None):

        super(Stopwatch, self).__init__(high_precision=high_precision)
        self.reset()

    def reset(self):
        self.__stop_time = None
        self.__laps = []
        self.__start_time = self._now

    def stop(self):
        if self.__stop_time is None:
            self.__stop_time = self._now

            return self.glance

        else:
            return self.__stop_time

    def lap(self):
        lap_end_time = self._now
        lap_start_time = (self.__start_time
                          if not self.__laps
                          else self.__laps[-1][u'lap_end_time'])
        self.__laps.append({
            u'lap_start_time': lap_start_time,
            u'lap_end_time':   lap_end_time,
            u'lap_time':       lap_end_time - lap_start_time
        })

        return self.__laps[-1][u'lap_time']

    @property
    def lap_times(self):
        return self.__laps

    @property
    def glance(self):
        if self.__stop_time:
            return self.__stop_time - self.__start_time

        else:
            return self._now - self.__start_time
