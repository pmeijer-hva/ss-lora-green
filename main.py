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
import modules.soundsensor as Soundsensor
#import random

# global variables
period = 0              # update periode in seconds for measuring a sending


led = Pin(machine.Pin.exp_board.G15,mode=Pin.OUT)
led.value(0)
UP_TIME = 15
DOWN_TIME = 60

def measure_sound(apin_sensor) -> int:
    adc = machine.ADC()             # create an ADC object for the sound sensor
    avg_sound = Soundsensor.running_average(apin_sensor)
    if avg_sound == None:
        avg_sound = 0
    return avg_sound

def measure_dht(sensor) -> list:
    #print("function measure")
    #global d
    #global hum, temp
    hum = 0
    temp = 0
    # measure DHT temp and hum values
    for _ in range(10):
        if d.trigger() == True:
            hum = d.humidity
            temp = d.temperature
            print("Humidity:", hum)
            print("Temperature: ",temp)
            return [hum, temp]
            
        else:
            print("STATUS: ",d.status)
            print(None, None)
            time.sleep(1)
           
    return [0,0]
    time.sleep(1)

    

def measure_light(apin_sensor) -> int:
    #global apin_lightsensor
    #global light

    light = apin_sensor
    if light != None:
        print("Light: ", light)
    else:
        print("Light: ",None)
        light = 0
    return light
    #time.sleep(5)

def measure_wind(sensor):
    #global Anemometer
    #global windspeed
    windspeed = 0
    if sensor != None:
        windspeed = sensor.get_windspeed()
        print("Windspeed", windspeed)
        
    else:
        windspeed = 0
        print("Windspeed:", None)

    return windspeed

# def measure():
#     hum = 0
#     temp = -40
#     #print("function measure")
#     global payload
#     global d
#     # measure DHT temp and hum values
#     if d.trigger() == True:
#         hum = d.humidity
#         temp = d.temperature
#         #temp = random.randrange(10, 40, 0.1)
#         #hum = random.randrange(0, 100, 0.1)
    
#         # encode
#         hum = int(hum * 10)                 # 2 Bytes
#         temp = int(temp*10) + 400           # max -40°, use it as offset
#         #print("temp: ", temp, "hum: ", hum)

#         ht_bytes = ustruct.pack('HH', hum, temp)
#         payload.append(ht_bytes[0])
#         payload.append(ht_bytes[1])
#         payload.append(ht_bytes[2])
#         payload.append(ht_bytes[3])
    
#         #print("payload written", payload)
#     # confirm with LED
#     # pycom.rgbled(0x0000FF)  # Blue
#     # time.sleep(0.1)
#     # pycom.rgbled(0x000000)  # Off
#     # time.sleep(1.9)
#     else:
#         print(d.status)
#         payload = []



# light sensor init
adc = machine.ADC()             # create an ADC object for the light sensor
#apin_lightsensor = adc.channel(pin='P13', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P13, 3.3V reference, 12bit

# anemometer init

print("starting main...")

def appendPayload(Bytes) -> list:
    payload = []
    for i in range(len(Bytes)):
        payload.append(Bytes[i])
    return payload

if __name__ == "__main__":
    sckt = join_lora()
    time.sleep(2)
    
    # global data buffer
    payload = []            # common data buffer to collect and send
    chrono = Timer.Chrono()
    chrono.start()
    led.value(1)

    # Sensors
    apin_soundsensor = adc.channel(pin='P13', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P13
    d = dht_module.device(machine.Pin.exp_board.G22)
    #apin_lightsensor = adc.channel(pin='P13', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P13, 3.3V reference, 12bit
    apin_lightsensor = None
    sensor_anemometer = Anemometer()
    sensing = True
    #while chrono.read() < UP_TIME:
    while sensing:
        print("TIME: ", chrono.read())
        #measure_dht()
        #measure_sound()
        time.sleep(2)

        # Data
        hum_temp = measure_dht(d)
        hum = hum_temp[0]
        temp = hum_temp[1]
        light = measure_light(apin_lightsensor)
        windspeed = measure_wind(None)
        sound = measure_sound(apin_soundsensor)

       
        # encode
        temp = int(temp * 10 ) + 400           # max -40°, use it as offset
        hum = int(hum * 10)                 # 2 Bytes
        lux = int(0 * 10)                 # 2 Bytes
        press = int(0 / 100)              # original value is in pA 
        ht_bytes = ustruct.pack('HHHH', temp, hum, lux, sound)

        payload = appendPayload(ht_bytes)
            
        print("[SENT] TEMP: {} | HUM: {} | DOLK \n".format(temp, hum))

            

       
        # payload = [0x01, 0x02, 0x03]
        if len(payload) != 0:
            print("LORA:", payload)
            send_lora(sckt, payload)
            print("SENT PAYLOAD: ", payload)
            payload = []
            
        else:
            print("EMPTY PAYLOAD")
        
        #sensing = False
        time.sleep(DOWN_TIME)


    print("[Going into a coma]")
    led.value(0)
    machine.deepsleep(DOWN_TIME*1000)
    
  