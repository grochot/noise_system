# encoding: utf-8

import time
import unittest
import datetime
import timeit
from timingsutil.timeout import Timeout


class TestConfiguration(unittest.TestCase):

    TOLERANCE = 0.005

    def now(self):
        return timeit.default_timer()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_timeout(self):

        timeout = Timeout(-1)
        self.assertLessEqual(timeout.seconds_remaining, 0)
        self.assertEqual(timeout.time_remaining, datetime.timedelta(seconds=0))
        self.assertTrue(timeout.expired)

        timeout = Timeout(0)
        self.assertEqual(timeout.seconds_remaining, 0)
        self.assertEqual(timeout.time_remaining, datetime.timedelta(seconds=0))
        self.assertTrue(timeout.expired)

        timeout = Timeout(5)
        self.assertGreaterEqual(timeout.seconds_remaining, 4)
        self.assertGreaterEqual(timeout.time_remaining, datetime.timedelta(seconds=4))
        self.assertFalse(timeout.expired)
        time.sleep(2)
        self.assertGreaterEqual(timeout.seconds_remaining, 2)
        self.assertGreaterEqual(timeout.time_remaining, datetime.timedelta(seconds=2))
        self.assertFalse(timeout.expired)
        time.sleep(3 + self.TOLERANCE)
        self.assertTrue(timeout.expired, timeout.seconds_remaining)

    def wait_check(self,
                   wait):
        start_time = self.now()
        Timeout(wait).wait()
        time_after_wait = self.now() + self.TOLERANCE
        self.assertGreaterEqual(time_after_wait,
                                start_time + wait,
                                start_time + wait - time_after_wait)

    def test_5s_timeout_wait(self):
        self.wait_check(5)

    def test_half_second_timeout_wait(self):
        self.wait_check(0.5)

    def test_timeout_not_expired(self):
        wait = 5
        start_time = self.now()
        iteration = 0
        timeout = Timeout(wait)

        while not timeout.expired:
            iteration += 1
            time.sleep(1)
            self.assertGreaterEqual(timeout.elapsed_time + self.TOLERANCE, iteration)
            self.assertGreaterEqual(timeout.seconds_remaining, 0)

        self.assertGreaterEqual(self.now(), start_time + wait)

    # TODO: Add tests for interruptable


if __name__ == u'__main__':
    unittest.main()
