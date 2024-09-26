# encoding: utf-8

import time
import unittest
from timingsutil import Stopwatch


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_stopwatch(self):

        stopwatch = Stopwatch()

        for _ in range(3):
            time.sleep(1)
            self.assertEqual(round(stopwatch.lap()), 1)

        self.assertEqual(round(stopwatch.stop()), 3)


if __name__ == u'__main__':
    unittest.main()
