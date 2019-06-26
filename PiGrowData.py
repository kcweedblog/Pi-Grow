import time
import board
import busio
import digitalio
from busio import I2C
import adafruit_bme680
import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import json
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# create the spi bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# create the cs (chip select)
cs = digitalio.DigitalInOut(board.D22)

# create the mcp object
mcp = MCP.MCP3008(spi, cs)

# create an analog input channel on pin 0
chan0 = AnalogIn(mcp, MCP.P0)
chan1 = AnalogIn(mcp, MCP.P1)
     
# Create library object using our Bus I2C port
i2c = I2C(board.SCL, board.SDA)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
     
# change this to match the location's pressure (hPa) at sea level
bme680.sea_level_pressure = 1013.25

iot_hub = "demo.thingsboard.io"
port = 1883
username="ENTER YOUR TOKEN HERE"
password=""
topic="v1/devices/me/telemetry"

client=mqtt.Client()
client.username_pw_set(username,password)
client.connect(iot_hub,port)
print("Connection success")

data=dict()
while True:   
	ctemp = bme680.temperature
	temp = ctemp * 9 / 5 + 32
	print("\nTemperature: %0.1f F" % temp)
	data["Temp: "]=temp
	print("Gas: %d ohm" % bme680.gas)
	data["Gas: "]=bme680.gas
	print("Humidity: %0.1f %%" % bme680.humidity)
	data["Humidity: "]=bme680.humidity
	print("Pressure: %0.3f hPa" % bme680.pressure)
	data["Pressure: "]=bme680.pressure
	print("Altitude = %0.2f meters" % bme680.altitude)
	data["Altitude: "]=bme680.altitude
	print('Raw ADC Value: ', chan1.value)
	print('ADC Voltage: ' + str(chan1.voltage) + 'V')
	data["Water Value: "]=chan1.value
	data["Water Voltage: "]=chan1.voltage
	data_out=json.dumps(data)
	client.publish(topic,data_out,0)
     
	time.sleep(10)
