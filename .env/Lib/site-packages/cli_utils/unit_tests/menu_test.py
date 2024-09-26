# -*- coding: utf-8 -*-

import logging_helper

logging = logging_helper.setup_logging(logger_name = __name__)
from cli_utils.menu import Menu


def check_binding(formal_p = u'actual was not supplied'):
    return u'|{formal}|'.format(formal = formal_p)

class CheckMenu(Menu):


    PARAMS1 = (Menu.param(formal = u'formal_p',
                          actual = u'False'),
               )

    PARAMS2 = (Menu.param(formal = u'formal_p',
                          actual = u'self.ivar1'),
               )

    IGNORE_RESULT = Menu.option(text     = u'ignore result',
                                function = check_binding)

    SET_IVAR1_TO_IVAR2 = Menu.option(text       = u'Set ivar1 to False',
                                     function   = check_binding,
                                     result     = u'ivar1',
                                     parameters = PARAMS1)

    SET_IVAR2_TO_IVAR1 = Menu.option(text       = u'Set ivar2 to ivar1',
                                     function   = check_binding,
                                     result     = u'ivar2',
                                     parameters = PARAMS2)

    RESET_VALUES = Menu.option(text       = u'reset values',
                               function   = u'self.reset',
                               result     = u'ivar2',
                               parameters = PARAMS2,
                               state      = Menu.OFF)

    OPTIONS = (IGNORE_RESULT,
               SET_IVAR1_TO_IVAR2,
               SET_IVAR2_TO_IVAR1,
               RESET_VALUES,)

    def __init__(self):
        self.reset()
        Menu.__init__(self)

    def reset(self):
        self.ivar1 = True
        self.ivar2 = False

    def refresh(self):
        print self.ivar1
        print self.ivar2
        if self.ivar1 == self.ivar2:
            Menu.set_option_state(self.RESET_VALUES)


if __name__ == u"__main__":
    CheckMenu().controller()