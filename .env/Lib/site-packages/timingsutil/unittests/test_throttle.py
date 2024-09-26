# encoding: utf-8

import unittest
import datetime
from timingsutil import Throttle


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_throttle(self):

        t = Throttle(2)

        self.assertEqual(t.interval, 0.5)

        for _ in range(5):
            current = datetime.datetime.now()
            t.wait()
            self.assertGreaterEqual(datetime.datetime.now(), current - datetime.timedelta(milliseconds=500))


if __name__ == u'__main__':
    unittest.main()
