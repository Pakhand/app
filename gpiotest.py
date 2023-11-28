import wiringpi
import time
import sys
from wiringpi import GPIO

NUM = 17    #26pin
#NUM = 18   #26pin
#NUM = 20   #for Orange Pi Zero 2
#NUM = 19   #for Orange Pi 4
#NUM = 28   #40pin

NUM = int(input("Used wPi mode,please input pinnum:"))
#pinval = int(input("please input pin value(1/0):"))

wiringpi.wiringPiSetup()


#for i in range(0, NUM):
wiringpi.pinMode(NUM, GPIO.OUTPUT) ;

while True:
    try:
        wiringpi.digitalWrite(NUM, GPIO.HIGH)
        time.sleep(1)
        wiringpi.digitalWrite(NUM, GPIO.LOW)    
        time.sleep(1)
    except KeyboardInterrupt:
        print("\nexit")
        sys.exit(0)