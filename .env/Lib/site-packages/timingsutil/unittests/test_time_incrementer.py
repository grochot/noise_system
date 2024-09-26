# encoding: utf-8

import unittest
import datetime
from timingsutil import TimeIncrementer


class TestTimeIncrementer(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_time_offseter_with_defaults(self):
        tinc = TimeIncrementer()
        PERIOD = TimeIncrementer.DEFAULT_PERIOD
        self.assertEqual(tinc._period.seconds, PERIOD)
        self.assertEqual(tinc.start, tinc.current)
        self.assertEqual((tinc.next() - tinc.start).seconds, PERIOD)
        self.assertEqual((tinc.current - tinc.start).seconds, PERIOD)
        self.assertEqual((tinc.next() - tinc.start).seconds, PERIOD * 2)
        self.assertEqual((tinc.current - tinc.start).seconds, PERIOD * 2)

    def test_non_default_period(self):
        PERIOD = 600
        tinc = TimeIncrementer(period=PERIOD)
        self.assertEqual(tinc._period.seconds, PERIOD)
        self.assertEqual(tinc.start, tinc.current)
        self.assertEqual((tinc.next() - tinc.start).seconds, PERIOD)
        self.assertEqual((tinc.current - tinc.start).seconds, PERIOD)
        self.assertEqual((tinc.next() - tinc.start).seconds, PERIOD * 2)
        self.assertEqual((tinc.current - tinc.start).seconds, PERIOD * 2)

    def test_timedelta_period(self):
        PERIOD = datetime.timedelta(minutes=8)
        tinc = TimeIncrementer(period=PERIOD)
        self.assertEqual(tinc._period, PERIOD)
        self.assertEqual(tinc.start, tinc.current)
        self.assertEqual((tinc.next() - tinc.start), PERIOD)
        self.assertEqual((tinc.current - tinc.start), PERIOD)
        self.assertEqual((tinc.next() - tinc.start), PERIOD * 2)
        self.assertEqual((tinc.current - tinc.start), PERIOD * 2)

    def test_string_start_without_format(self):
        self.assertRaises(ValueError, TimeIncrementer, start=u"10:00")

    def test_string_start_with_bad_format(self):
        self.assertRaises(ValueError,
                          TimeIncrementer,
                          start=u"10:00",
                          fmt=u"%H")

    def test_string_start_with_good_format(self):
        tinc = TimeIncrementer(start=u"10:00",
                               fmt=u"%H:%M")
        PERIOD = TimeIncrementer.DEFAULT_PERIOD
        self.assertEqual(tinc._period.seconds, PERIOD)
        self.assertEqual(tinc.start, tinc.current)
        self.assertEqual(tinc.start, u"10:00")
        self.assertEqual(tinc.next(), u"10:05")
        self.assertEqual(tinc.current, u"10:05")
        self.assertEqual(tinc.next(), u"10:10")
        self.assertEqual(tinc.current, u"10:10")


if __name__ == u'__main__':
    unittest.main()
