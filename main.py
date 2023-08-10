import machine
from machine import Pin
from modules import dht_module, lightsensor, anemometer
from modules.anemometer import Anemometer
import time
import pycom
import _thread
from modules.lora_module import join_lora, send_lora
import ustruct
from machine import Timer
from modules.soundsensor import *
#import random

# global variables
period = 0              # update periode in seconds for measuring a sending

hum = None
temp = None
light = None
windspeed = None

led = Pin(machine.Pin.exp_board.G15,mode=Pin.OUT)
led.value(0)
UP_TIME = 15
DOWN_TIME = 60

def measure_sound():
    adc = machine.ADC()             # create an ADC object for the sound sensor
    apin_soundsensor = adc.channel(pin='P13', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P13
    avg_sound = running_average()
    print(avg_sound)
    #time.sleep(periode)

def measure_dht():
    #print("function measure")
    global d
    global hum, temp
    # measure DHT temp and hum values
    if d.trigger() == True:
        hum = d.humidity
        temp = d.temperature
        print("Humidity:", hum,  "Temperature: ",temp)
        
    else:
        print(d.status)
        print(None, None)
    time.sleep(1)

    #return(hum, temp)

def measure_light():
    global apin_lightsensor
    global light

    light = apin_lightsensor()
    if light != None:
        print("Light: ", light)
    else:
        print("Light: ",None)
    #time.sleep(5)

def measure_wind():
    global Anemometer
    global windspeed

    if windspeed != None:
        windspeed = sensor_anemometer.get_windspeed()
        
        print("Windspeed", windspeed)
    else:
        print("Windspeed:", None)

def measure():
    hum = 0
    temp = -40
    #print("function measure")
    global payload
    global d
    # measure DHT temp and hum values
    if d.trigger() == True:
        hum = d.humidity
        temp = d.temperature
        #temp = random.randrange(10, 40, 0.1)
        #hum = random.randrange(0, 100, 0.1)
    
        # encode
        hum = int(hum * 10)                 # 2 Bytes
        temp = int(temp*10) + 400           # max -40°, use it as offset
        #print("temp: ", temp, "hum: ", hum)

        ht_bytes = ustruct.pack('HH', hum, temp)
        payload.append(ht_bytes[0])
        payload.append(ht_bytes[1])
        payload.append(ht_bytes[2])
        payload.append(ht_bytes[3])
    
        #print("payload written", payload)
    # confirm with LED
    # pycom.rgbled(0x0000FF)  # Blue
    # time.sleep(0.1)
    # pycom.rgbled(0x000000)  # Off
    # time.sleep(1.9)
    else:
        print(d.status)
        payload = []



# light sensor init
adc = machine.ADC()             # create an ADC object for the light sensor
apin_lightsensor = adc.channel(pin='P13', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P13, 3.3V reference, 12bit

# anemometer init
sensor_anemometer = Anemometer()

print("starting main")


if __name__ == "__main__":
    sckt = join_lora()
    time.sleep(2)
    MESURE = 0
    # global data buffer
    payload = []            # common data buffer to collect and send
    d = dht_module.device(machine.Pin.exp_board.G22)
    chrono = Timer.Chrono()
    chrono.start()
    led.value(1)
    while chrono.read() < UP_TIME:
        print("TIME: ", chrono.read())
        measure_dht()
        measure_sound()
        time.sleep(2)
        if hum != None and temp != None:
            # encode
            temp = int(temp * 10 ) + 400           # max -40°, use it as offset
            hum = int(hum * 10)                 # 2 Bytes
            lux = int(0 * 10)                 # 2 Bytes
            press = int(0 / 100)              # original value is in pA 
            ht_bytes = ustruct.pack('HHHH', temp, hum, lux, press)

            payload = []
               
            payload.append(ht_bytes[0])
            payload.append(ht_bytes[1])
            payload.append(ht_bytes[2])
            payload.append(ht_bytes[3])
            payload.append(ht_bytes[4])
            payload.append(ht_bytes[5])
            payload.append(ht_bytes[6])
            payload.append(ht_bytes[7])


            print("[SENT] TEMP: {} | HUM: {} | DOLK \n".format(temp, hum))

            hum = None
            temp = None
            light = None
            windspeed = None

       
        # payload = [0x01, 0x02, 0x03]
        if len(payload) != 0:
            print("LORA:", payload)
            send_lora(sckt, payload)
            print("SENT PAYLOAD: ", payload)
            payload = []
            
        else:
            print("EMPTY PAYLOAD")

    print("[Going into a coma]")
    led.value(0)
    machine.deepsleep(DOWN_TIME*1000)
  