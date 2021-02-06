
#for audiocontrol2 plugins e.g. https://github.com/hifiberry/audiocontrol2/blob/master/ac2/plugins/control
from RPi import GPIO
#TODO: should we import this or embed it?
from gpiozero import MCP3008

import logging
from typing import Dict

from ac2.plugins.control.controller import Controller
from usagecollector.client import report_usage

class PowerPot(Controller):

    def __init__(self, params: Dict[str, str]=None):
        super().__init__()

        self.pwr=26
        self.vol=0
        self.step=0.02

        self.volume=0
        self.power=None


        self.name = "powerpot"

        if params is None:
            params={}

        #pwr indicates the GPIO pin used for "on/off"
        if "pwr" in params:
            try:
                self.pwr = int(params["pwr"])
            except:
                logging.error("can't parse %s",params["pwr"])


        #vol indicates the analogue channel on mcp3008
        if "vol" in params:
            try:
                self.vol = int(params["vol"])
            except:
                logging.error("can't parse %s",params["vol"])

        #step indicates minimum change to cause a volume adjustment
        if "step" in params:
            try:
                self.step = int(params["step"])
            except:
                logging.error("can't parse %s",params["step"])


        logging.info("initializing power/volume controller on GPIOs "
                     " pwr=%s, vol=%s%%",
                     self.pwr, self.vol)

        GPIO.setup(self.pwr, GPIO.IN)

        self.adc = MCP3008(self.vol)


    def run(self):
        #self.encoder.watch()
        while True:
            #take a reading
            new_power = GPIO.input(self.pwr)
            #if the last reading was low and this one high, print
            if (self.power == None):
                if not new_power:
                    print("starting in on")
                else:
                    print("starting in off")
            elif self.power != new_power:
                if not input:
                    print("Turned on")
                else:
                    print("Turned off")
                    if self.playercontrol is not None:
                        self.playercontrol.pause_all()
                        report_usage("audiocontrol_pot_power", 1)
                    else:
                        logging.info("no player control, ignoring pot power")

            #update previous input
            self.power = new_power

            #new_volume = 0
            if (self.adc.value < 0.002):
                new_volume = 0
            else:
                new_volume = round(self.adc.value,2)

            if (self.volume != new_volume and abs(new_volume - self.volume)>self.step):
                self.volume = new_volume
                print(" volume ", self.volume)
                if self.volumecontrol is not None:
                    self.volumecontrol.set_volume(self.volume * 100)#set_volume accepts 0-100
                    report_usage("audiocontrol_pot_volume", 1)
                else:
                    logging.info("no volume control, ignoring pot volume")


            #slight pause to debounce
            time.sleep(0.2)