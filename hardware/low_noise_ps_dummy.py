from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from time import sleep

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LowNoisePSDummy(Instrument):
    def __init__(self, adapter, read_termination="\n", **kwargs):
        pass

    def enabled(self):
        pass
   
    def disabled(self):
        pass

    def voltage_setpoint(self, vol = 0): 
       pass
    

    voltage = 0

    def run_to_zero(self): 
       pass



    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.values(":system:error?")
        if len(err) < 2:
            err = self.read()  # Try reading again
        code = err[0]
        message = err[1].replace('"', "")
        return (code, message)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("SIM928 reported error: %d, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for SIM 928 error retrieval.")

    def shutdown(self):
        pass
