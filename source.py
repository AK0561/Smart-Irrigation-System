import RPi.GPIO as GPIO
import datetime
import spidev
import time

# Create SPI connection
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000  # 1 MHz

# Function to read out data from MCP3008
def readData(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

pinPump = 4  # GPIO pin of pump
needsWater = 630  # sensor value for dry air

# General GPIO settings
GPIO.setwarnings(False)  # Ignore warnings (irrelevant here)
GPIO.setmode(GPIO.BCM)  # Refer to GPIO pin numbers
GPIO.setup(pinPump, GPIO.OUT)  # Pi can send voltage to pump
GPIO.output(pinPump, GPIO.LOW)  # Turn the pump off

# Read moisture data from channel 0
moisture = readData(0)

# Write time and current moisture in the statistics file
f = open("/home/pi/WateringStats.txt", "a")
currentTime = datetime.datetime.now()
f.write(str(currentTime) + ":\n")

# 450 = 780 - 330, moisture in %
f.write("Current moisture: " + str(round((moisture - 330) / 450 * 100, 2)) + "% (" + str(moisture) + ")\n")

# If plants are too dry, start pumping and record the moisture in the file
if moisture > needsWater:
    t_end = time.time() + 4  # Pump runs for 4 seconds
    
    # Actual pumping
    while time.time() < t_end:
        GPIO.output(pinPump, GPIO.HIGH)
        GPIO.output(pinPump, GPIO.LOW)  # Turn the pump off

    f.write("Plants got watered!\n")
    
f.write("\n")  # Line break for the next log entry
f.close()  # Close the file

# Properly clean up used GPIO pins
GPIO.cleanup()
