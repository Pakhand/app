#!/usr/bin/python  
# -*- coding:utf-8 -*-

import OPi.GPIO as GPIO
import time

IO_set_list = []
Unavailable_IO_num = [1,2,4,6,9,14,17,20,25]
NOut=15
# 13 - 2

def Io_init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)   # Код доски
    # GPIO.setmode (GPIO.BCM) # Кодировка BCM
    # GPIO.setmode (GPIO.SUNXI) # Кодировка WPI

def Get_user_input():
    pinnum =  13 #int(input("Used BOARD mode,please input pinnum(0-26):"))
    #while pinnum < 0 or pinnum > 26 or pinnum in Unavailable_IO_num:
    #    print('Incorrect input or Unavailable IO,try again')
    #    pinnum = int(input("Used BOARD mode,please input pinnum(0-26):"))
    IO_set_list.append(pinnum)
    
    pinval = 1 #int(input("please input pin value(1/0):"))
    #while pinval not in [0,1]:
     #   print('Incorrect input,try again')
     #   pinval = int(input("please input pin value(1/0):"))
    IO_set_list.append(pinval)
    
    return IO_set_list

def IO_out():
    print("welcom")
    Io_init()
    Get_user_input()
    GPIO.setup(IO_set_list[0], GPIO.OUT)
    GPIO.setup(NOut, GPIO.IN)
    GPIO.output(IO_set_list[0],IO_set_list[1])

def main():
    #os.system(`gpio-readall`)
    IO_out()
    #GPIO.cleanup()

#if __name__ == '__main__':
 #   try:
main()
    #except KeyboardInterrupt:
   # except:
    #    GPIO.cleanup()
   # finally:
   #     GPIO.cleanup()

    
while True:
    try:
        #wiringpi.digitalWrite(NUM, GPIO.HIGH)
        GPIO.output(IO_set_list[0],0)
        if GPIO.input(NOut):
            print('Input was HIGH')
        else:
            print('Input was LOW')

        time.sleep(1)
        #wiringpi.digitalWrite(NUM, GPIO.LOW)    
        if GPIO.input(NOut):
            print('Input was HIGH')
        else:
            print('Input was LOW')
        GPIO.output(IO_set_list[0],1)
        time.sleep(1)
    except KeyboardInterrupt:
        print("\nexit")
        GPIO.cleanup()
        sys.exit(0)