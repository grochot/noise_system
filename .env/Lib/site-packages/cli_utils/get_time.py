# encoding: utf-8
#

from cli_utils import Quit
from datetime import date, timedelta
from timingsutil import daylight_savings
from timingsutil.jdutil import datetime, mjd_to_datetime

SIXTY_DAYS = timedelta(days=60)

try:
    raw_input
    input = raw_input  # Py2. rename raw_input to align with Py3
except NameError:
    pass  # Py 3 already has input

#
#                     ┌─────────────────┐
#                     │     GET TIME    │
#                     └─────────────────┘
#


def date_and_time_to_datetime(string):
    # convert from "2016-12-03 15:50"
    return (datetime.strptime(string,
                              u'%Y-%m-%d %H:%M')
            - daylight_savings.TIME_OFFSET)


def date_and_time_with_tz_to_datetime(string):
    # convert from "2016-12-03T15:50:00Z"
    return (datetime.strptime(string,
                              u'%Y-%m-%dT%H:%M:%SZ')
            - daylight_savings.TIME_OFFSET)


def time_to_datetime(string):
    temp_date_time_string = (u'{date} {time}'
                             .format(date=date.today().strftime(u"%Y-%m-%d"),
                                     time=string))

    return date_and_time_to_datetime(temp_date_time_string)


def mjd_string_to_datetime(string):
    return mjd_to_datetime(float(string)) # MJD is in UTC


def parse_date_and_time(date_time_string):

    for fn in (date_and_time_to_datetime,
               date_and_time_with_tz_to_datetime,
               time_to_datetime,
               mjd_string_to_datetime
               ):
        try:
            return fn(date_time_string)
        except (ValueError, OverflowError, TypeError):
            pass
    raise ValueError(u'{date_time_string} is not a valid date'
                     .format(date_time_string=date_time_string))


# TODO: create real test
if __name__ == u"__main__":
    assert parse_date_and_time(u'19:00') != None, u''
    assert parse_date_and_time(u'2015-03-02 19:00') != None, u''
    assert parse_date_and_time(u'2015-03-02T19:00:00Z') != None, u''
    try:
        parse_date_and_time(u'19:00x')
        assert False
    except ValueError:
        pass
    assert parse_date_and_time(u'57083.5') != None, u''


def format_date_and_time(date_time):
    return datetime.strftime(date_time, u'%Y-%m-%d %H:%M')


def get_time(message=u'Enter a data and time',
             default_time=None,
             quit_value=u'Q',
             non_time_valid_values=None,
             allow_times_before_default_or_now=True,
             exclude_values=None,
             additional_validation=None,
             return_action=None,
             valid_window=SIXTY_DAYS):
    """
    Uses raw_input to read event times in 'YYYY-MM-DD HH:MM' format.
    Hitting return returns None.
    Values are converted to MJD Time.

    :param: message: Used to make the prompt more explicit.
    :param: default_time: can be used to prevent stale values
    :param: allow_quit: lets the user bail out.
    :param: allow_times_before_default_or_now: can be used to prevent
            stale values
    :param: additional_validation: can be used to perform additional checks.
            can be a simple function with a single datetime parameter or
            can be a dictionary:
                {u'function'        : <function object>,
                 u'time param name' : <name of the formal parameter that
                                       takes the time value.
                                       Omit this if it's u'time' >,
                 u'<param name 1>'  : <param value 1>
                 ...
                 u'<param name n>  : <param value n>}
    """
    event_time = None

    exclude_values = ([]
                      if exclude_values is None
                      else exclude_values)

    non_time_valid_values = ([]
                             if non_time_valid_values is None
                             else non_time_valid_values)

    return_action = u'' if return_action is None else return_action

    allow_quit = quit_value is not None

    quit_value = u'Q' if quit_value is None else quit_value

    if allow_quit is True:
        if quit_value == u'':
            return_action = (u'return to quit'
                             if not return_action
                             else return_action)
        else:
            return_action = (u"'{quit_value}' to quit"
                             .format(quit_value=quit_value)
                             if not return_action
                             else return_action)

    if default_time is not None:
        return_action = (u'return for {default_time}'
                         .format(default_time=default_time))

    return_action = (u' ({return_action}) '
                     .format(return_action=return_action))

    while not event_time:
        event_time = (input(u"{message} <YYYY-MM-DD> HH:MM {rtrn_action}> "
                            .format(message=message,
                                    rtrn_action=return_action))
                      .strip().lower())

        if event_time == u"":
            if default_time is not None:
                return default_time

        if allow_quit and event_time.lower() == quit_value.lower():
            raise Quit(u'Quitting get_time')

        if event_time in non_time_valid_values:
            return event_time
        try:
            event_time = parse_date_and_time(date_time_string=event_time)
        except ValueError:
            event_time = None
            print(u"\nThat's a bad datetime.\n"
                  u"Examples: Date and Time : 2016-03-02 18:00\n"
                  u"              Time only : 18:00\n"
                  u"               MJD Time : 57083.736111\n"
                  u"Please try again.")
            continue

        if event_time in exclude_values:
            print(u'That value is not permitted. Try again.')
            event_time = None
            continue

        if additional_validation is not None:
            if additional_validation.__class__ == {}.__class__:
                params = {key: value
                          for key, value in iter(additional_validation.items())
                          if key not in (u'function',
                                         u'time param name')}

                time_formal_parameter_name = (
                    additional_validation.get(u'time param name', u'time'))

                params[time_formal_parameter_name] = event_time
                additional_validation[u'function'](**params)
            else:
                additional_validation(event_time)

        now = datetime.now()

        if not allow_times_before_default_or_now:
            if default_time is not None:
                if event_time <= default_time:
                    event_time = None
                    print(u'Time must be at or after {d_and_t}. '
                          u'Try again.'
                          .format(d_and_t=format_date_and_time(default_time)))

            elif event_time <= now:
                event_time = None
                print(u'Time must be at or after {d_and_t}. Try again.'
                      .format(d_and_t=format_date_and_time(now)))

        if valid_window is not None:
            start_of_valid_window = now - valid_window
            end_of_valid_window   = now + valid_window

            if not start_of_valid_window < event_time < end_of_valid_window:

                print(u'\n\nTime is outside a sensible window '
                      u'relative the the current date.')

                print(u'Time should be between {sovw} '
                      u'and {eovw}. Please try again\n'\
                      .format(sovw=format_date_and_time(start_of_valid_window),
                              eovw=format_date_and_time(end_of_valid_window)))

    return event_time
