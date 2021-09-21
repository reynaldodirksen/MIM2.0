#!/usr/bin/python3         

import matplotlib.pyplot as plt
import numpy as np
import signal                   
import sys
import RPi.GPIO as GPIO
from time import sleep
from libs.micronas import USBProgrammer
GPIO.setmode(GPIO.BCM)
SWITCH_GPIO1 = 26
switchHeight = 13
SWITCH_GPIO2 = 19
cilinder = 16
button = 4
LED_GPIO = 12
hor_var = True
vert_var = True
GPIO.setup(switchHeight, GPIO.IN) # eesx498 1
GPIO.setup(23, GPIO.OUT) #dir Mrot
GPIO.setup(24, GPIO.OUT) #sig Mrot
GPIO.setup(26, GPIO.IN) # eesx498 1
GPIO.setup(9, GPIO.OUT) #dir Mheight
GPIO.setup(27, GPIO.OUT) #sig Mheight
GPIO.setup(19,  GPIO.IN)# eesx498 2
GPIO.setup(12, GPIO.OUT) # sig UV led
#GPIO.setup(16, GPIO.OUT) # sig cilinder
GPIO.setup(4, GPIO.IN)    # sig Switch
GPIO.setup(14, GPIO.OUT) # EnMrot
GPIO.setup(15, GPIO.OUT) # EnMheight
GPIO.setup(cilinder, GPIO.OUT)

micronas = USBProgrammer('/dev/ttyUSB1')
def move_vert(steps, direction):
        GPIO.output(15, True)
        if direction == 'U':
            GPIO.output(9, True)
            
        elif direction == 'D':
            GPIO.output(9, False)
        sleep(0.1)
        RotationPosition = 0
        pauze = 0.00001
        while RotationPosition <= steps:
            RotationPosition += 1
            GPIO.output(27, True)
            sleep(pauze)
            GPIO.output(27, False)
            sleep(pauze)
        GPIO.output(15, False)
def move_hor(steps, direction):
        GPIO.output(14, True)
        if direction == 'R':
            GPIO.output(23, True)
            
        elif direction == 'L':
            GPIO.output(23, False)
        sleep(0.1)
        RotationPosition = 0
        pauze = 0.00001
        while RotationPosition <= steps:
            RotationPosition += 1
            GPIO.output(24, True)
            sleep(pauze)
            GPIO.output(24, False)
            sleep(pauze)
        GPIO.output(14, False)
        
def move_hor_indefinite(direction):
    pauze = 0.00001
    GPIO.output(14, True)
    if direction == 'R':
        GPIO.output(23, True)
            
    elif direction == 'L':
        GPIO.output(23, False)
    while(hor_var):
        GPIO.output(24, True)
        sleep(pauze)
        GPIO.output(24, False)
        sleep(pauze)
        
        
def move_vert_indefinite(direction):
    pauze = 0.00001
    GPIO.output(15, True)
    if direction == 'U':
        GPIO.output(9, True)
            
    elif direction == 'D':
        GPIO.output(9, False)
    while(vert_var):
        GPIO.output(27, True)
        sleep(pauze)
        GPIO.output(27, False)
        sleep(pauze)

def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def switch_callback_hor(channel):
    global hor_var
    hor_var = False
    
def switch_callback_vert(channel):
    global vert_var
    vert_var = False

#def coefficient(x,y):
#    x_1 = x[0]
#    x_2 = x[1]
#    x_3 = x[2]
#    y_1 = y[0]
#    y_2 = y[1]
#    y_3 = y[2]
#
#    a = y_1/((x_1-x_2)*(x_1-x_3)) + y_2/((x_2-x_1)*(x_2-x_3)) + y_3/((x_3-x_1)*(x_3-x_2))
#
#    b = (-y_1*(x_2+x_3)/((x_1-x_2)*(x_1-x_3))
#         -y_2*(x_1+x_3)/((x_2-x_1)*(x_2-x_3))
#         -y_3*(x_1+x_2)/((x_3-x_1)*(x_3-x_2)))
#
#    c = (y_1*x_2*x_3/((x_1-x_2)*(x_1-x_3))
#        +y_2*x_1*x_3/((x_2-x_1)*(x_2-x_3))
#        +y_3*x_1*x_2/((x_3-x_1)*(x_3-x_2)))
#
#    return a,b,c            


GPIO.setup(switchHeight, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(switchHeight, GPIO.BOTH,
        callback=switch_callback_vert)
signal.signal(signal.SIGINT, signal_handler)

GPIO.setup(SWITCH_GPIO2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_GPIO, GPIO.OUT)   

GPIO.add_event_detect(SWITCH_GPIO2, GPIO.BOTH, 
        callback=switch_callback_hor)
    
signal.signal(signal.SIGINT, signal_handler)
while(1):
    
    GPIO.output(LED_GPIO, 1)
    GPIO.output(cilinder, 0)
#    move_vert(20000, 'U')
#    sleep(200)
#    sleep(2000)
    
    
    move_hor(0, 'L')
    move_vert(0, 'D')
    sleep(1)
#    

    
    
    if GPIO.input(switchHeight):
        move_vert_indefinite('U')
    else:
        move_vert_indefinite('D')
        
    
    move_vert(40000, 'D')
#    if GPIO.input(19):
#        move_hor(6000, 'L')
    
#    signal.pause()
#    sleep(100)
    move_hor_indefinite('L')
    
    
    while(GPIO.input(button) == 0):
        a = 0
    
    VList = [0]
    stepList = [0]
    GPIO.output(cilinder, 1)
    setup = micronas.read_setup()
    setup['mrange'] = 3
    setup['sensitivity'] = 64
    setup['offset'] = 0
    setup['tc'] = 6
    setup['tcsq'] = 0
    micronas.write_setup(setup)
    move_vert(5000, 'U')
    sleep(1)
    move_hor(4000, 'L')
    sleep(1)
    move_hor(1000, 'R')
    sleep(1)
    lastVoltage = 5
    count = 0
    for i in range(1000):
        move_hor(100, 'R')
        Voltage = micronas.read_voltage_out()
        if Voltage > lastVoltage:
            count+=1
            if count >= 3:
                print('hello')
                break
                
        else:
            lastVoltage = Voltage
            count = 0
        print(Voltage, lastVoltage)
              
    for i in range(1000):
        move_hor(50, 'R')
        Voltage = micronas.read_voltage_out()
        print(Voltage)
        if Voltage >= 1.6:
            break
#    move_vert(3200, 'U' )
    sleep(1)
    oldV = micronas.read_voltage_out()
    
    count = 0
    totstep = 0
    VList = []
    
    counterB = 0
    counter = 0
    vals = [0] *3
    maxDeltaV = 0
    stepList = []

        
    step = 3000 
    lastV = 0
    setup['mrange'] = 7
    micronas.write_setup(setup)
    for i in range(60):
        move_vert(step, 'U')
        totstep +=step
        Voltage = micronas.read_voltage_out_times(5)
        VList.append(Voltage)
        stepList.append(totstep)
        print(Voltage, totstep)
        
        if totstep > 20000:
            if oldV-Voltage < 0.02:
                break
        oldV = Voltage
        if Voltage < 0.01:
            print("V too low")
            break
#                for i in range(100):
#                    move_hor(100, 'R')
#                volt = micronas.read_voltage_out_times(5)
#                if volt > 2:
#                    oldV = volt
#                    stepList.clear()
#                    VList.clear()
#                    totstep = 0
#                    break
        
      
    for i in range(100):
        
        x = np.array(stepList[-10:])
        y = np.array(VList[-10:])
        z = np.polyfit(x, y, 2)
        a = z[0]
        b = z[1]
        c = z[2]
        p = np.poly1d(z)
        xp = np.linspace(0, totstep, 100)
        _ = plt.plot(x, y, '.', xp, p(xp), '-', xp, p(xp), '--')
        plt.ylim(0,5)
        plt.show()
        minsteps = -(b/(2*a))
        print('minstep = ', minsteps)
        deltastep = minsteps-totstep
        if deltastep < 30:
            break
        else:
            if deltastep > 6000:
                deltastep = 3000 
            move_vert(round(deltastep/2), 'U')
            totstep +=round(deltastep/2)
            Voltage = micronas.read_voltage_out_times(5)
            if Voltage < 0.01:
                print('mag too close')
                break
            VList.append(Voltage)
            stepList.append(totstep)
            print(Voltage, totstep)
        
    Voltage = micronas.read_voltage_out_times(5)
    if Voltage > 1.6:
        for i in range(500):
            move_hor(50, 'L')
            print(micronas.read_voltage_out())
            Voltage = micronas.read_voltage_out()
            if Voltage < 1.6:
                break
            
    elif Voltage < 1.4:
        for i in range(500):
            move_hor(50, 'R')
            print(micronas.read_voltage_out())
            Voltage = micronas.read_voltage_out()
            if Voltage > 1.4:
                break
    print(micronas.read_voltage_out())
    
    
    for i in range(1000):
        move_hor(50, 'R')
        Voltage = micronas.read_voltage_out()
        print(Voltage, '>3.8')
        if Voltage > 3.8:
            break
    
    for i in range(1000):
        move_hor(100, 'L')
        Voltage = micronas.read_voltage_out()
        print(Voltage, '<3.5')
        if Voltage < 3.5:
            steps = 0
            V35 = micronas.read_voltage_out_times(5)
            break
    for i in range(1000):
        move_hor(50, 'L')
        steps +=50
        Voltage = micronas.read_voltage_out()
        print(Voltage, '<1.5')
        if Voltage < 1.5:
            V15 = micronas.read_voltage_out_times(5)
            break
    vps = (V35-V15)/steps
    print(V35, V15, steps, vps)
    MR0 = (micronas.read_setup()['mrange'] +1)
    MR1 = round((vps*MR0)/(0.013*0.65))
    setup['mrange'] = MR1-1
    GPIO.output(cilinder, 0)
#    micronas.write_setup(setup)
#    newVoltage = 2.5+((V15-2.5)*(MR0/MR1))
#    print((MR0-1), (MR1-1))
#    print(newVoltage)
#    if newVoltage <0:
#        for i in range(1000):
#            move_hor(100, 'R')
#            Voltage = micronas.read_voltage_out()
#            print(Voltage)
#            if Voltage <0.5:
#                break
#    for i in range(1000):
#        move_hor(30, 'R')
#        Voltage = micronas.read_voltage_out_times(3)
#        print(Voltage)
#        if Voltage > 0.1:
#            print(Voltage)
#            break
#    for i in range(1000):
#        move_hor(25, 'R')
#        Voltage = micronas.read_voltage_out_times(3)
#        print(Voltage)
#        if Voltage > 0.85:
#            print(Voltage)
#            break
    
    
#    sleep(2)
#    GPIO.output(LED_GPIO, 1)
#    sleep(20)
#    GPIO.output(cilinder, 0)
#    GPIO.output(LED_GPIO, 0)
#    
#    print(micronas.read_voltage_out())
        
    while(micronas.read_id() != "0000 0000"):
        a = 2
    sleep(10)
    hor_var = True
    vert_var = True
    sleep(1)    
    

        
        