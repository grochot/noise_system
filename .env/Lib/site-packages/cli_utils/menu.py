# encoding: utf-8
#
import copy
import logging
from cli_utils import Quit


#
#                     ┌────────────────────────┐
#                     │     MENU BASE CLASS    │
#                     └────────────────────────┘
#


class Menu(object):

    """
    Menu is intended to be sublassed.

    Class level OPTIONS tuple should be provided.

    Each entry in OPTIONS should be an option, which is a dictionary:
        {TEXT      : <string to be used for the menu option>
         STATE     : <initial state. ON or OFF>
         FUNCTION  : <function object to be called when the option is selected>
         PARAMETERS: <tuple of parameters>
         RESULT    : <string describing the instance variable to hold the result
                      of the call>
         }

    There is a helper function (option) to help create these.

    Each parameter in the PARAMETERS tuple is a dictionary:
        {FORMAL : <name of a formal parameter of FUNCTION,
         ACTUAL : <an expression to be evaluated or a value>
         }
    There is also helper function (param) for creating parameters

    If the visibility of options needs to modified, this can be done
    by overloading the refresh method and calling:
         set_option_stat
         set_options_states
         enable_option
         disable_option

    """
    TEXT = u'text'
    RESULT = u'result'
    FUNCTION = u'function'
    PARAMETERS = u'params'
    STATE = u'state'
    FORMAL = u'formal'
    ACTUAL = u'actual'

    ON = True
    OFF = False
    QUIT = u'quit'

    @staticmethod
    def quit_is_indicated(string):
        string = string.lower().strip()
        return string != u'' and string == u'quit'[:len(string)]

    @staticmethod
    def param(formal,
              actual):

        return {Menu.FORMAL: formal,
                Menu.ACTUAL: actual}

    @staticmethod
    def option(text,
               function,
               result=None,
               parameters=None,
               state=None):

        return {Menu.TEXT:       text,
                Menu.FUNCTION:   function,
                Menu.RESULT:     result,
                Menu.PARAMETERS: parameters,
                Menu.STATE:      Menu.ON if state is None else state}

    def __init__(self,
                 message=u'',
                 allow_quit=True):

        try:
            self.options = copy.deepcopy(self.OPTIONS)
        except:
            raise NotImplementedError(u'OPTIONS must be declared '
                                      u'when subclassing Menu')
        self.options_text = []
        for option in self.options:
            if option[Menu.TEXT] not in self.options_text:
                self.options_text.append(option[Menu.TEXT])
            else:
                raise ValueError(u'Duplicate Menu option declared:"{text}"'
                                 .format(text=option[Menu.TEXT]))

        self.allow_quit = allow_quit
        self.message = message

    @staticmethod
    def option_enabled(option):
        return option[Menu.STATE] is Menu.ON

    def get_option_by_index(self,
                            index):
        try:
            pick = self.options[int(index) - 1]
        except ValueError:
            raise ValueError(u'invalid option')
        if not self.option_enabled(pick):
            raise ValueError(u'invalid option')
        return pick

    def get_option(self,
                   keep_trying=True):

        # Loop until we get a a good value
        invalid_choice = False
        while True:        # Print out the enabled menu options
            print(u'\n\n{message}\n'
                  .format(message=self.message))
            for index, option in enumerate(self.options):
                if self.option_enabled(option):
                    print(u'{n:{w}d}. {option_text}'
                          .format(n=index + 1,
                                  w=len(str(len(self.options))),
                                  option_text=option[self.TEXT]))

            if invalid_choice:
                invalid_choice = False
                pick = (raw_input(u'\n'
                                  u'Invalid option. '
                                  u'Please try again{quit_text} > '
                                  .format(quit_text=u' ("Q" to quit)'
                                          if self.allow_quit else u''))
                        .strip().lower())
            else:
                pick = (raw_input(u'\nEnter your choice{quit_text} > '
                                  .format(quit_text=u' (u"Q" to quit)'
                                          if self.allow_quit else u''))
                        .strip().lower())

            if self.quit_is_indicated(pick):
                raise Quit()
            try:
                return self.get_option_by_index(pick)

            except ValueError:
                invalid_choice = True
                if not keep_trying:
                    raise ValueError(u'invalid option')

    def get_option_index(self,
                         option):
        try:
            return self.options_text.index(option[Menu.TEXT])
        except TypeError:
            return self.options_text.index(option)

    def __option(self,
                 option):
        return self.options[self.get_option_index(option)]

    def set_option_state(self,
                         option,
                         state):
        state = Menu.ON if state in (True, Menu.ON) else Menu.OFF
        self.__option(option)[Menu.STATE] = state

    def set_options_states(self,
                           options,
                           state):
        for option in options:
            self.set_option_state(option=option,
                                  state=state)

    def enable_option(self,
                      option):
        self.__option(option)[Menu.STATE] = Menu.ON

    def disable_option(self,
                       option):
        self.__option(option)[Menu.STATE] = Menu.OFF

    def refresh(self):
        pass

    def __actual(self,
                 actual):
        try:
            exec(u'actual = {actual}'.format(actual=actual))
        except Exception:
            pass
        return actual

    def __params(self,
                 option):
        if option[Menu.PARAMETERS] is not None:
            return {param[Menu.FORMAL]: self.__actual(param[Menu.ACTUAL])
                    for param in option[Menu.PARAMETERS]}

        return {}

    def controller(self):

        try:
            while True:

                self.refresh()

                pick = self.get_option()

                function = pick[Menu.FUNCTION]
                params = self.__params(pick)

                try:
                    result = function(**params)
                except Exception:
                    logging.exception(u'Error in {function}({params})'
                                      .format(function=function,
                                              params=params))
                    continue

                if pick[Menu.RESULT] is not None:
                    setattr(self, pick[Menu.RESULT].split(u'self.')[-1], result)

        except Quit:
            pass
