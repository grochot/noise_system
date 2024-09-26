# encoding: utf-8

import timeit
import datetime
import time
import logging
from .time_constants import (ONE_HOUR,
                             TEN_MINUTES,
                             ONE_MINUTE,
                             TEN_SECONDS,
                             TWENTY_SECONDS,
                             ONE_SECOND)


class TimersBase(object):

    def __init__(self,
                 high_precision=None):
        self.__high_precision = high_precision == True
        self.__old_now = timeit.default_timer()

    @property
    def _now(self):

        """
        Returns a time elapsed value. It's just an elapsed time since the
        timer started rather than a clock value
        :return: seconds since timer started (float)
        """
        if self.__high_precision:
            new_now = timeit.default_timer()
        else:
            new_now = time.time()
        if new_now < self.__old_now:
            raise(RuntimeError('Timer overflow'))
        self.__old_now = new_now
        return new_now


class Timeout(TimersBase):

    def __init__(self,
                 seconds=0,
                 start_time_offset=0,
                 start_in_an_expired_state=False,
                 interrupt_period=None,
                 high_precision=None):

        """
        Re-usable timeouts with reporting.
        
        :param seconds:
        :param start_time_offset:
        :param start_in_an_expired_state:
        :param interrupt_period: Allows Timeout.expire to interrupt a wait
                                 after the given time. Must be > 0.
                                 If > seconds, is set to seconds, which
                                 effectively makes it not interruptable!
        :param high_precision: Uses timeit.clock to provide μs accuracy on Windows

        WARNING:
        """

        super(Timeout, self).__init__(high_precision=high_precision)

        if seconds < 0:
            logging.warning(u'Timeout initialised with a negative value. Using 0s instead.')
            seconds = 0
        self.__timeout_length = seconds
        self.__start_time_date = datetime.datetime.now()
        self.__start_time = self._now + start_time_offset

        self.__end_time = self.__start_time
        self.interrupted = False
        if not start_in_an_expired_state:
            self.__end_time += self.__timeout_length

        self.__expired = None
        if interrupt_period is not None:
            if interrupt_period <= 0:
                raise ValueError(u'interrupt_period must be > 0 (value:{i})'
                                 .format(i=self.__interrupt_period))

            self.__interrupt_period = (interrupt_period
                                       if interrupt_period < seconds
                                       else seconds)
        else:
            self.__interrupt_period = seconds

    @property
    def expired(self):
        if not self.__expired:
            self.__expired = self._now >= self.__end_time

        return self.__expired

    def expire(self):
        if not self.__expired:
            self.__end_time = self.__start_time
            self.__expired = True

    def interrupt(self):
        self.interrupted = True
        self.__expired = True

    def restart(self):
        self.__start_time_date = datetime.datetime.now()
        self.__start_time = self._now
        self.__end_time = self.__start_time + self.__timeout_length
        self.__expired = False
        self.interrupted = False

    def wait_and_restart(self,
                         message=None):
        self.wait(message=message)
        self.restart()

    @property
    def elapsed_time(self):
        return self._now - self.__start_time

    @property
    def seconds_remaining(self):
        if self.__expired or self.__timeout_length <= 0:
            logging.debug(u'seconds remaining:{sr}'.format(sr=0))
            return 0

        logging.debug(u'end_time:{et}; reference_timer:{tc}'
                      .format(et=self.__end_time,
                              tc=self._now))

        time_remaining = self.__end_time - self._now

        if time_remaining > self.__timeout_length or time_remaining < 0:
            self.__expired = True
            logging.debug(u'seconds remaining:{sr}'.format(sr=0))
            return 0

        logging.debug(u'seconds remaining:{sr}'.format(sr=time_remaining))
        return time_remaining

    @property
    def time_remaining(self):
        return datetime.timedelta(seconds=self.seconds_remaining)

    def __interruptable_wait(self,
                             wait_time):
        while not self.interrupted and wait_time > 0:
            sleep_time = (self.__interrupt_period
                          if self.__interrupt_period < wait_time
                          else wait_time)
            logging.debug(u'non interruptable wait: {sleep_time}'.format(sleep_time=sleep_time))
            try:
                time.sleep(sleep_time)
            except TypeError:
                pass # TODO: Fox this. Problem with self.__interrupt_period = None
            wait_time -= sleep_time

    def wait(self,
             message=None):

        if message is None:
            if not self.expired:
                wait_time = self.seconds_remaining
                if self.__interrupt_period is None:
                    logging.debug(u'non interruptable wait: {sleep_time}'.format(sleep_time=wait_time))
                    time.sleep(wait_time)
                else:
                    self.__interruptable_wait(wait_time)
        else:
            while not self.expired:
                remaining = self.time_remaining.seconds

                # print rather than log as this gives a live
                # progress to the user for very long intervals
                # but is not relevant in logs.
                print(u'{message} in {minutes}m {seconds}s.'
                      .format(message=message,
                              minutes=remaining // 60,
                              seconds=remaining % 60))

                if remaining > ONE_HOUR:
                    if remaining > ONE_HOUR + TEN_MINUTES:
                        Timeout(ONE_HOUR,
                                interrupt_period=True).wait()
                    else:
                        self.__interruptable_wait(ONE_HOUR - TEN_MINUTES)

                elif remaining > TEN_MINUTES:
                    self.__interruptable_wait(TEN_MINUTES)

                elif remaining > ONE_MINUTE:
                    self.__interruptable_wait(ONE_MINUTE)

                elif remaining < TEN_SECONDS:
                    self.__interruptable_wait(ONE_SECOND)

                else:
                    self.__interruptable_wait(TEN_SECONDS
                                              if remaining >= TWENTY_SECONDS
                                              else remaining - TEN_SECONDS)

            print(u'Wait finished.')
