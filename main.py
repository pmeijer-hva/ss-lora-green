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


UP_TIME = 15
DOWN_TIME = 60

#Function used for mesuring sound
def measure_sound(apin_sensor) -> int:
    adc = machine.ADC()             # create an ADC object for the sound sensor
    avg_sound = Soundsensor.running_average(apin_sensor) #Gets average sound
    print("Sound: ", avg_sound)
    if avg_sound == None:
        avg_sound = 0
        
    return avg_sound #returns the average

#Function used for mesuring temp and hum
def measure_dht(sensor) -> list:
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
            time.sleep(1)
           
    return [0,0]
    time.sleep(1)  

#Function used for mesuring light
def measure_light(apin_sensor) -> int:
    lightVal = 0
    light = apin_sensor
    if light != None:
        print("Light: ", apin_sensor())
        lightVal = apin_sensor()
    else:
        print("Light: ",None)
        lightVal = 0
    return lightVal #Returns the light
    #time.sleep(5)

#Function used for mesuring wind
def measure_wind(sensor):
    windspeed = 0
    if sensor != None:
        windspeed = sensor.get_windspeed() #Gets the windspeed
        print("Windspeed", windspeed)
        
    else:
        windspeed = 0
        print("Windspeed:", None)

    return windspeed #Returns the windspeed

#Function used to collect all the measurments
def get_measurement() -> list:
            # Data
        print("[STARTING ALL MEASURE]")
        try:
            print("\t[START MEASURING TEMP & HUM]")
            hum_temp = measure_dht(d) #Gets a list of hum and temp
            hum = hum_temp[0] # The hum
            temp = hum_temp[1]# The temp
        except:
            print("Grande Problemas with hum or temp!")
        
        try:
            print("\t[START MEASURING LIGHT]")
            light = measure_light(apin_lightsensor) #Light
        except:
            print("Grande problemas with the light!")

        try:
            print("\t[START MEASURING WINDSPEED]")
            windspeed = measure_wind(None) #Windspeed
        except:
            print("Grande problemas with windspeed")
        
        try:
            print("\t[START MEASURING sound]")
            sound = measure_sound(apin_soundsensor) #Sound

        except:
            print("Grande problemas with the sound")

        
        print("\t[END MEASURING]")

        ht_bytes = pack_ht_bytes(temp, hum, light, sound) #A list of the packed bytes
        return ht_bytes #Return the packed bytes

#Function that takes in temp, hum, light and sound as a parameter
#calculates all the right measurment and Then pack everything  
def pack_ht_bytes(temprature, humidity, light, sounds) -> list:
        # encode
        temp = int(float(temprature) * 10 ) + 400    # max -40°, use it as offset
        hum = int(float(humidity) * 10)              # 2 Bytes
        lux = int(float(light) * 10)                 # 2 Bytes
        press = int(0 / 100)                         # original value is in pA 
        sound = int(float(sounds))
        ht_bytes = ustruct.pack('HHHHHH', temp, hum, lux, sound) #packs the variable

        return ht_bytes #Return the packed bytes


# light sensor init
adc = machine.ADC()             # create an ADC object for the light sensor

# anemometer init

print("starting main...")

#Function used for append the payload
def appendPayload(Bytes) -> list:
    payload = []
    for i in range(len(Bytes)):
        payload.append(Bytes[i])
    return payload

#Main
if __name__ == "__main__":
    sckt = join_lora()
    time.sleep(2)
    
    # global data buffer
    payload = []            # common data buffer to collect and send
    chrono = Timer.Chrono() # Initializaition of a timer
    chrono.start() # Starts the timer
    # led.value(1)

    # Sensors
    apin_soundsensor = adc.channel(pin='P13', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P13
    d = dht_module.device(machine.Pin.exp_board.G22)
    light_ADC = machine.ADC()
    apin_lightsensor = light_ADC.channel(pin='P15', attn = machine.ADC.ATTN_11DB)   # create an analog pin on P15, 3.3V reference, 12bit
    sensor_anemometer = Anemometer() #The anemometer
    sensing = True # A boolean variable gets switched when a sensor is not a sensing

    while sensing:

        packed_ht_bytes = get_measurement()
        payload = appendPayload(packed_ht_bytes)
            
       
        if len(payload) != 0: #If the payload the is not empty
            send_lora(sckt, payload) #Sends the payload 
            print("SENT PAYLOAD: ", payload)
            payload = []
            
        else:
            print("EMPTY PAYLOAD")
        
        print("\n[GOING TO SLEEP]\n")
        time.sleep(DOWN_TIME)


    print("[Going into a coma]")
    # led.value(0)
    machine.deepsleep(DOWN_TIME*1000) #Deepsleep
    
  