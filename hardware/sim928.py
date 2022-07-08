from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SIM928(Instrument):
    def __init__(self, adapter, read_termination="\n", **kwargs):
        super().__init__(
            adapter,
            "SRS Sim928 Voltage Source" ,
            read_termination=read_termination,
            **kwargs
        )

    enabled = Instrument.control(
        "EXON?",
        "EXON %d",
        """A boolean property that controls whether the source is enabled, takes
        values True or False.""",
        validator=strict_discrete_set,
        values={"ON": 1, "OFF": 0},
        map_values=True,
    )


    voltage_setpoint = Instrument.control(
        "VOLT?",
        "VOLT %g",
        """A floating point property that controls the source voltage
        in volts. This is not checked against the allowed range. Depending on
        whether the instrument is in constant current or constant voltage mode,
        this might differ from the actual voltage achieved.""",
    )


    voltage = Instrument.measurement(
        "VOLT?",
        """Reads the voltage (in Volt) the dc power supply is putting out.
        """,
    )



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
        """ Disable output, call parent function"""
        self.enabled = False
        super().shutdown()
