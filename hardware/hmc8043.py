from pymeasure.instruments import Instrument
from time import sleep, time
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HMC8043(Instrument):

    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            resourceName,
            "HMC8043",
            includeSCPI=True,
            **kwargs
        )
        # Read twice in order to remove welcome/connect message

    maximumfield = 1.00
    maximumcurrent = 50.63

    # coilconst = Instrument.control(
    #     "COIL?", "CONF:COIL %g",
    #     """ A floating point property that sets the coil contant
    #     in kGauss/A. """
    # )

    set_channel = Instrument.control(
        "INST:NSEL?",
        "INST:NSEL %g",
        """A floating point property that controls the source voltage
        in volts. This is not checked against the allowed range. Depending on
        whether the instrument is in constant current or constant voltage mode,
        this might differ from the actual voltage achieved.""",
    )
   
    enable_channel = Instrument.control(
        "OUTP?",
        "OUTP %g",
        """A boolean property that controls whether the source is enabled, takes
        values True or False. The convenience methods :meth:`~.HMC8043.enable_source` and
        :meth:`~.HMC8043.disable_source` can also be used.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )


    set_voltage = Instrument.control(
        "VOLT?", "VOLT %g",
        """ A floating point property that sets the voltage limit
        for charging/discharging the magnet. """
    )

    

    # @property
    # def magnet_status(self):
    #     STATES = {
    #         1: "RAMPING",
    #         2: "HOLDING",
    #         3: "PAUSED",
    #         4: "Ramping in MANUAL UP",
    #         5: "Ramping in MANUAL DOWN",
    #         6: "ZEROING CURRENT in progress",
    #         7: "QUENCH!!!",
    #         8: "AT ZERO CURRENT",
    #         9: "Heating Persistent Switch",
    #         10: "Cooling Persistent Switch"
    #     }
    #     return STATES[self.state]

    # def ramp_to_current(self, current, rate):
    #     """ Heats up the persistent switch and
    #     ramps the current with set ramp rate.
    #     """
    #     self.enable_persistent_switch()

    #     self.target_current = current
    #     self.ramp_rate_current = rate

    #     self.wait_for_holding()

    #     self.ramp()

    # def ramp_to_field(self, field, rate):
    #     """ Heats up the persistent switch and
    #     ramps the current with set ramp rate.
    #     """
    #     self.enable_persistent_switch()

    #     self.target_field = field

    #     self.ramp_rate_field = rate

    #     self.wait_for_holding()

    #     self.ramp()

    # def wait_for_holding(self, should_stop=lambda: False,
    #                      timeout=800, interval=0.1):
    #     """
    #     """
    #     t = time()
    #     while self.state != 2 and self.state != 3 and self.state != 8:
    #         sleep(interval)
    #         if should_stop():
    #             return
    #         if (time() - t) > timeout:
    #             raise Exception("Timed out waiting for AMI430 switch to warm up.")

    def shutdown(self):
        """ Turns on the persistent switch,
        ramps down the current to zero, and turns off the persistent switch.
        """
        self.disable_channel()