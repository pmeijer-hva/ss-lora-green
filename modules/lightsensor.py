# this module reads the analog light sensor from seeeds
# via an analog input port
# 2022 - Martin Vogel - HLSU martin.vogel@hslu.ch

import machine
import time



if __name__ == "__main__":
    adc = machine.ADC()             # create an ADC object for the light sensor
    apin_lightsensor = adc.channel(pin='P15', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P13
    while True:
        try:
            lightval = apin_lightsensor()
            print(lightval)
        except:
            print("cannot read light sensor")
        time.sleep(1)
