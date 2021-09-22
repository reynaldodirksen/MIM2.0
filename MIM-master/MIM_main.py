# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 15:10:42 2019

@author: user
"""
import matplotlib.pyplot as plt
import numpy as np      
import RPi.GPIO as GPIO
from kivy.config import Config
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from libs.micronas import USBProgrammer
from time import sleep
import libs.databaseFunctions as databaseFunctions
Count = 0
sensor1 = 26
sensor2 = 19 
sensor3 = 13
UV =    21
Cilinder =  16
PushButton = 4
sensor3 = 99
#GPIO.setup(sensor1, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Sens1
#GPIO.setup(sensor2, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Sens2
#GPIO.setup(sensor3, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Sens3
GPIO.setup(PushButton, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #Switch
GPIO.setup(UV, GPIO.OUT) # UV LED
GPIO.setup(Cilinder, GPIO.OUT) #Cilinder led
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
SWITCH_GPIO1 = 26
switchHeight = 13
SWITCH_GPIO2 = 19
cilinder = 16
button = 4
LED_GPIO = 21

GPIO.setup(switchHeight, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) # eesx498 1
GPIO.setup(23, GPIO.OUT) #dir Mrot
GPIO.setup(24, GPIO.OUT) #sig Mrot
GPIO.setup(26, GPIO.IN) # eesx498 1
GPIO.setup(9, GPIO.OUT) #dir Mheight
GPIO.setup(27, GPIO.OUT) #sig Mheight
GPIO.setup(19,  GPIO.IN)# eesx498 2
GPIO.setup(21, GPIO.OUT) # sig UV led
#GPIO.setup(16, GPIO.OUT) # sig cilinder
GPIO.setup(4, GPIO.IN)    # sig Switch
GPIO.setup(14, GPIO.OUT) # EnMrot
GPIO.setup(15, GPIO.OUT) # EnMheight
GPIO.setup(cilinder, GPIO.OUT)




Builder.load_string('''
<RootWidget>:
    Screen:
        name: 'MIM'
        Spinner:
            id: operator_select
            text: "Select operator"       #default value showed
            values: root.user()
            on_text: root.setUser(self.text)
            pos: 400, 100
            size_hint: None, None
            size: 200, 50
            
        Spinner:
            id: order_select
            text: "Select Order"       #default value showed
            values: root.order()
            on_text: root.showSpecs(self.text)
            pos: 100, 100
            size_hint: None, None
            size: 200, 50
        
    
        Label:
            text: "Product: "
            id: productNumber
            pos: 380, -10
            font_size: 30
            
        Label:
            text: "MO: "
            id: orderNumber
            pos: 380, -50
            font_size: 30
        Label:
            text: "QTY: "
            id: amountNumber
            pos: 380, -90
            font_size: 30
        Image:
            source: 'libs/idbikelogo2black.jpg'
            size_hint: 1, 1
            pos: 0, 300
    
        
        Label:
            text: 'Select Order and Operator'
            id: progress
            font_size: '30sp'
            pos: -100, 0
            
        Label:
            id: voltage
            font_size: '25sp'
            pos: -100, -60
            
        Label:
            id: range
            font_size: '25sp'
            pos: -100, -120
            
        Label:
            id: sensitivity
            font_size: '25sp'
            pos: -100, -180
        Button:
            text: 'exit app'
            pos: 0, 450
            size_hint: None, None
            size: 100, 50
            on_press: root.stop_app()
            
        Label:
            pos: 550, 190
            id: version
        Button:
            size_hint: None, None
            pos: 1000, 100
            size: 200,50
            text: 'reset bit position'
            on_release: root.reset_height()
            id: reset
            
''')


class TouchInput(Widget):
    def on_touch_down(self, touch):
        print(touch)
    
    def on_touch_move(self, touch):
        print(touch)
    
    def on_touch_up(self, touch):
       print(touch)
    
    

class RootWidget(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_condition = [0, 0]
        GPIO.output(LED_GPIO, 0)
        GPIO.output(cilinder, 0) 
        global hor_var
        hor_var= True
        global vert_var
        vert_var = True
        self.finished = True
        self.ids.version.text = 'MIM 2.0'
        

        
        self.count2 = 0
        
        #add variables and callback to the software
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(button, GPIO.RISING, callback=self.button_callback, bouncetime = 200)
        self.StationID = 1
        self.micronas = USBProgrammer('/dev/ttyUSB0')
        self.disableStart = [0, 0]
        self.stationID = 7
        self.move_hor(0, 'L')
        self.move_vert(0, 'U')
#        start by setting bit position to zero
        self.move_vert_indefinite('D')
##        
##    
#        self.move_vert(100000, 'U')
        
        self.move_hor_indefinite('L')
        self.vertsteps = 0
        self.newplate = 0
        
        
        
        
        
    #this function is used to fill in the drop down menu in kivy
    def user(self):
        return databaseFunctions.returnOperators()  
        
    #this function is used to fill in the drop down menu in kivy
    def order(self):
        return databaseFunctions.returnOrders()
    #internally save the chosen operator
    def setUser(self, text):
        self.operator = text
        self.start_condition[0] = 1
        self.ids.progress.text = "Connect next sensor and press start button"
        
        
    #display the relevant information of the chosen order/product
    def showSpecs(self, order):
        self.order = order
        self.productInfo = databaseFunctions.returnProductInfo(self.order)
        self.orderInfo = databaseFunctions.returnOrderInfo(self.order)
        self.product = self.productInfo[2]
        self.ids.productNumber.text = "Product: "+ str(self.productInfo[2])
        self.ids.orderNumber.text = "MO: " + str(self.order)
        self.ids.amountNumber.text = "QTY: " + str(self.orderInfo[4])
        self.sensw = self.productInfo[5]
        self.ZTVw = self.productInfo[8]
        self.start_condition[1] = 1
        
        #program the initial values for a sensor
    def programDefaults(self):
        self.setup = self.micronas.read_setup()
        self.setup['tc'] = int(self.productInfo[11])
        self.setup['tcsq'] = int(self.productInfo[12])
        self.setup['offset'] = 0
        self.setup['sensitivity'] = 64
        self.setup['mrange'] = 3
        #export that the sensor has been connected to a MIM/SUAMSetup
        databaseFunctions.exportSensor(self.setup['version'], self.micronas.read_id())
        self.micronas.write_setup(self.setup)
        
        #what to do when we have an error
    def error(self, errorText):
        #show the error
        self.ids.progress.text = errorText
        #turn off UV and air pressure
        GPIO.output(cilinder, 0)
        GPIO.output(UV, 0)
        self.ids.reset.disabled = False
        self.finished = True
        #export the error to database
        databaseFunctions.addIncident(self.stationID, self.operator, self.order, self.micronas.read_id(), errorText, self.ids.version.text)
        
    
        
    #main function
    def main(self, state):
        #when button is pressed we start the main at state 1
        if state == 1:
            self.ids.reset.disabled = True
            #check if we have sensor connected and magnet position
            if self.checkErrors(1):
                self.programDefaults()
                if self.checkErrors(2):
                    self.find_minimum()           
                else:
                    self.error(self.myError)
                    
                    return
            else:
                self.error(self.myError)
                return
            
        
            
        
        #initial curve setting
        elif state == 2:
            #begin with MR=160 so we dont go under 0V when settng height
            self.setup['mrange'] = 7
            self.micronas.write_setup(self.setup)
            self.stepList = []
            self.totstep = 0
            self.VList = []
            self.step = 3000 
            self.ids.progress.text = "setting height"
            #move upwards in steps of 3000
            for i in range(60):
                
                self.move_vert(self.step, 'U')
                sleep(0.05)
                #track steps
                self.vertsteps +=self.step
                self.totstep +=self.step
                #if steps > 120000 we cant move further up
                if self.vertsteps > 250000:
                    break
                Voltage = self.micronas.read_voltage_out_times(5)
                #fill in Voltage and steps in a list that we will use to calculate the proper height
                self.VList.append(Voltage)
                self.stepList.append(self.totstep)
                self.ids.voltage.text = str(Voltage) + 'V'
                #if our deltaV is small enoough we can move to calculating the bottom of the curve
                if self.totstep > 20000:
                    if self.oldV-Voltage < 0.02 and Voltage < 2:
                        break
                self.oldV = Voltage
                #voltage too low means we cannot reach the perfect height 
                if Voltage < 0.08:
                    self.ids.voltage.text = "V too low"
                    break
            if self.vertsteps > 250000:
                self.myError = "Can't move bit higher"
                self.error(self.myError)
            elif Voltage < 0.08:
                self.myError = "Height error: Voltage under 0V"
                self.error(self.myError)
            else:
                self.main(3)
        
        #calculation of minimum in the curve
        elif state == 3:
            self.oldV = self.micronas.read_voltage_out()
            Voltage = self.oldV
            for i in range(100):
                
                #use np arrays and calculations to determine the curve and minimum points
                x = np.array(self.stepList[-10:])
                y = np.array(self.VList[-10:])
                z = np.polyfit(x, y, 2)
                a = z[0]
                b = z[1]
#                p = np.poly1d(z)
#                xp = np.linspace(0, self.totstep, 100)
#                _ = plt.plot(x, y, '.', xp, p(xp), '-', xp, p(xp), '--')
#                plt.ylim(0,5)
#                plt.show()
                minsteps = -(b/(2*a))
                deltastep = minsteps-self.totstep
                #if we are within 150 steps of minimum, we are good enough
                if deltastep < 6000:
                    break
                else:
                #if we arent within 150 steps, move vert steps/2 if it would be less than 1500 steps, else we move 1500 steps
                    if deltastep > 6000:
                        deltastep = 3000 
                    self.move_vert(round(deltastep/2), 'U')
                    #keep track of steps sow e dont pass max height and motor gets stuck
                    self.vertsteps +=round(deltastep/2)
                    self.totstep +=round(deltastep/2)
                    Voltage = self.micronas.read_voltage_out_times(5)
                    if Voltage < 0.08:
                        break
                    if Voltage > self.oldV:
                        break
                    #add new values to the list that we use to calculate the minimum
                    self.VList.append(Voltage)
                    self.stepList.append(self.totstep)
                    self.ids.voltage.text = str(Voltage)+ 'V'
                    self.oldV = Voltage
            if Voltage < 0.08:
                self.myError = 'mag too close'
                self.error(self.myError)
            else:
                self.move_vert(300, 'D')
                self.main(5)
            
        #we skip this in the MIM
        elif state == 4:
            Voltage = self.micronas.read_voltage_out_times(5)
            if Voltage > 1.6:
                for i in range(500):
                    
                    self.move_hor(50, 'L')
                    sleep(0.05)
                    Voltage = self.micronas.read_voltage_out()
                    if Voltage < 1.6:
                        break
            
            elif Voltage < 1.4:
                for i in range(500):
                    
                    self.move_hor(50, 'R')
                    sleep(0.05)
                    Voltage = self.micronas.read_voltage_out()
                    if Voltage > 1.4:
                        break
            
        #move right until we reach a voltage > 3.8V
        elif state == 5:
            sleep(0.3)
            self.setup['mrange'] = 5
            self.micronas.write_setup(self.setup)
            self.ids.progress.text = "setting magnet to 4V"
            for i in range(1000):
                
                self.move_hor(50, 'R')
                sleep(0.05)
                Voltage = self.micronas.read_voltage_out()
                self.ids.voltage.text = str(Voltage)+ 'V'
                if Voltage > 3.8:
                    break
            self.main(6)
            
        #move left until we are lower than 3.5V so we get the extra steps out    
        elif state == 6:
            self.ids.progress.text = "setting magnet to 3.5V"
            for i in range(1000):
                
                self.move_hor(100, 'L')
                sleep(0.05)
                Voltage = self.micronas.read_voltage_out()
                self.ids.voltage.text = str(Voltage)+ 'V'
                if Voltage < 3.5:
                    self.steps = 0
                    #keep good track of Voltage(5 measurements)
                    self.V35 = self.micronas.read_voltage_out_times(5)
                    break
            self.main(7)
        #move to < 1.5V and track steps
        elif state == 7:
            self.ids.progress.text = "setting magnet to 1.5V"
            for i in range(1000):
                
                self.move_hor(50, 'L')
                sleep(0.05)
                self.steps +=50
                Voltage = self.micronas.read_voltage_out()
                self.ids.voltage.text = str(Voltage)+ 'V'
                if Voltage < 1.5:
                    #keep good track of Voltage(5 measurements)
                    self.V15 = self.micronas.read_voltage_out_times(5)
                    break
            #we have a sensitivity here related to VPS(Volt per stap)
            self.vps = (self.V35-self.V15)/self.steps
            print(self.V35, self.V15, self.steps, self.vps)
            #newplate IS ONLY EVER 1 WHEN SETTING UP A NEW PLATE
            if self.newplate == 1:
                GPIO.output(cilinder, 0)
                print("VPSW for this plate = (Sensitivityw * ", self.vps, ")/SUAM Sensitivity")
            else:
                self.programFinalRange()
            
        #set magnet to ZTV=ZTVw
        elif state == 8:
            self.ids.progress.text = "setting magnet to final position"
            self.newVoltage = 2.5+((self.V15-2.5)*(((self.MR0)/(self.mrange))))
            if self.newVoltage <0.8:
                for i in range(1000):
                    
                    self.move_hor(50, 'R')
                    sleep(0.05)
                    Voltage = self.micronas.read_voltage_out()
                    self.ids.voltage.text = str(Voltage)    + 'V'
                    if Voltage <0.5:
                        break
            
                for i in range(1000):
                    
                    self.move_hor(10, 'R')
                    sleep(0.05)
                    Voltage = self.micronas.read_voltage_out()
                    self.ids.voltage.text = str(Voltage)    + 'V'
                    if Voltage > 0.2:
                        break
            for i in range(1000):
                
                self.move_hor(5, 'R')
                sleep(0.05)
                Voltage = self.micronas.read_voltage_out()
                self.ids.voltage.text = str(Voltage)    + 'V'
                if Voltage > 1.1*self.ZTVw:
                    break
            self.main(9)
        #display end results
        elif state == 9:
            sleep(1)
            for i in range(100):
                GPIO.input(button)
            self.setup = self.micronas.read_setup()
            #read ZTV and calculate sensitivity
            self.ZTV = round(self.micronas.read_voltage_out(), 2)
            self.sens = round(self.sens*self.sensw, 2)
            self.MR = (self.setup['mrange']+1)*20
            self.sensitivity = self.setup['sensitivity']
            self.ids.voltage.text = "ZTV: " + str(self.ZTV) + "V"
            self.ids.range.text = "Magnetic Range: " + str(self.MR)
            self.ids.sensitivity.text = "Approximate sensitivity: " + str(self.sens)
            if self.MR == 20:
                self.ids.range.color = 1,0,0,1
                self.myError = 'Magnetic Range 20 not allowed'
                self.ids.sensitivity.text = "reset bit before next sensor"
                self.error(self.myError)
                
                
            else:
                self.ids.range.color = 0,1,0,1
                self.exportValuesDB()
                self.main(10)
        #turn on UV for 10 seconds and let the pressure valve go
        elif state == 10:
            self.move_hor(50, 'L')

            GPIO.output(UV, 1)
            sleep(10)
            GPIO.output(UV, 0)
            self.move_vert(30000, 'D')
            self.ids.progress.text = "Positioning completed"
            GPIO.output(cilinder, 0)
            #wait until the cable to the sensor is removed
            while(self.micronas.read_id() != "0000 0000"):
                self.ids.voltage.text = "ZTV: " + str(self.micronas.read_voltage_out()) + "V"
                sleep(0.1)
            sleep(10)
            #10 seconds after removing the cable, reset height
            self.reset_height()
            
            
    def checkErrors(self, state):
        if state == 1:
            if self.micronas.read_id() == '0000 0000':
                self.myError = 'No sensor connected'
                return False
            
            else:
                return True
            
        if state == 2:
            #if at right pos beginning
            Voltage = self.micronas.read_voltage_out()
            if  Voltage == 2.51:
                self.myError = 'No magnet in sensor'
                return False
            else:
                return True
            
    #find minimum at beginning so we are in good working area
    def find_minimum(self):
        GPIO.output(cilinder, 1)
        sleep(1.5)
        self.ids.progress.text = "Finding minimum Voltage"
        self.move_vert(5000, 'U')
        sleep(1)
        self.move_hor(5000, 'L')
        sleep(1)
        self.move_hor(2500, 'R')
#        sleep(1)
#        self.lastVoltage = 5
#        self.count = 0
#        for i in range(1000):
#            self.move_hor(50, 'R')
#            Voltage = self.micronas.read_voltage_out()
#            if Voltage > self.lastVoltage:
#                self.count+=1
#                self.count2 = 0
#                if self.count >= 3:
#                    break
#                
#            elif Voltage == self.lastVoltage:
#                self.lastVoltage = Voltage
#                self.count = 0
#                self.count2 +=1
#            else:
#                self.lastVoltage = Voltage
#                self.count = 0
#                self.count2 = 0
#            if self.count2 > 15:
#                break
#            self.ids.voltage.text = str(Voltage) + 'V'
#        if self.count2 >= 15:
#            self.myError = "Magnet is not positioned on bit properly"
#            self.error(self.myError)
#        else:
        self.main(2)
        

        

        

    #calculate the end MR and sensitivity based on VPS and VPSW(sensw)
    def programFinalRange(self):
        sleep(1)
        self.vps = (self.V35-self.V15)/self.steps
        self.vpsw = databaseFunctions.returnVPSW(self.product)
        self.MR0 = self.setup['mrange']+1
        self.mrange = round((self.vps*self.MR0)/(self.vpsw*0.60))
        self.setup['mrange'] = self.mrange-1
        self.micronas.write_setup(self.setup)
        self.vps = self.vps*(self.MR0/self.mrange)
        self.sens = (self.vps/self.vpsw)
        self.setup['sensitivity'] = round((self.vpsw/self.vps)*self.setup['sensitivity'])
        self.vps = self.vps*(self.setup['sensitivity']/64)
        self.micronas.write_setup(self.setup)
        self.sens = self.sens*(self.setup['sensitivity']/64)
        self.main(8)
        
    
        
        #reset to default bit position, reset the variables
    def reset_height(self):
        self.ids.progress.text = "Setting bit to default position"
        sleep(0.5)
        self.ids.range.text = ''
        self.ids.voltage.text = ''
        self.ids.sensitivity.text = ''
        global hor_var
        hor_var = True
        global vert_var
        vert_var= True
        self.finished = True
        self.move_vert_indefinite('D')
        
        
        for i in range(100):
            GPIO.input(button)
        self.vertsteps = 0
        self.move_hor_indefinite('L')
        self.ids.progress.text = "Connect next sensor and press start button"
        self.ids.reset.disabled = False
        
    #export measures values to database
    def exportValuesDB(self):
        self.setup = self.micronas.read_setup()
        databaseFunctions.exportValues(self.micronas.read_id(), self.stationID, self.operator, self.order, self.setup['tc'], self.setup['tcsq'], self.setup['mrange'],self.setup['sensitivity'], self.setup['offset'], self.vps, self.sens, self.ZTV)
        
        
     
    #horizontal movement function definition
    def move_hor(self, steps, direction):
        GPIO.output(14, True)
        if direction == 'R':
            GPIO.output(23, True)
            
        elif direction == 'L':
            GPIO.output(23, False)
        sleep(0.1)
        RotationPosition = 0
        pauze = 0.00001
        while RotationPosition < steps:
            RotationPosition += 1
            GPIO.output(24, True)
            sleep(pauze)
            GPIO.output(24, False)
            sleep(pauze)
        GPIO.output(14, True)
        #vertical movement fucntion definition
    def move_vert(self, steps, direction):
        GPIO.output(15, True)
        if direction == 'U':
            GPIO.output(9, True)
            
        elif direction == 'D':
            GPIO.output(9, False)
        sleep(0.1)
        RotationPosition = 0
        pauze = 0.00001
        while RotationPosition < steps:
            RotationPosition += 1
            GPIO.output(27, True)
            sleep(pauze)
            GPIO.output(27, False)
            sleep(pauze)
        GPIO.output(15, True)
        
        
    def move_hor_indefinite(self, direction):
        pauze = 0.000001
        global hor_var
        GPIO.output(14, True) 
        if direction == 'R':
            GPIO.output(23, True)
            
        elif direction == 'L':
            GPIO.output(23, False)
        while(GPIO.input(SWITCH_GPIO2)) == False:
            GPIO.output(24, True)
            sleep(pauze)
            GPIO.output(24, False)
            sleep(pauze)
        
        
    def move_vert_indefinite(self, direction):
        pauze = 0.000001
        counter = 0
        global vert_var
        GPIO.output(15, True)
        if direction == 'U':
            GPIO.output(9, True)
            while(1):
                var = (GPIO.input(switchHeight))
                if var == 0:
                    counter +=1
                if counter >= 5:
                    break
                GPIO.output(27, True)
                sleep(pauze)
                GPIO.output(27, False)
                sleep(pauze)
            
        elif direction == 'D':
            GPIO.output(9, False)
            while(1):
                var = GPIO.input(switchHeight)
                if var == 1:
                    counter +=1
                if counter >= 5:
                    break
                GPIO.output(27, True)
                sleep(pauze)
                GPIO.output(27, False)
                sleep(pauze)
        
        

    
    
    
    #when button gets pressed to start main
    def button_callback(self, channel):
        for i in range(10):
            GPIO.input(button)
        if self.ids.reset.disabled == True:
            return
        if self.start_condition == [1, 1]:
            if self.finished == True:
                self.ids.progress.text = "programming default values"
                self.finished = False
                self.main(1)
                
        else:
            self.ids.progress.text = "Please select Order and Operator\nbefore pressing the button"
    def stop_app(self):
        MIM.get_running_app().stop()
class MIM(App):
    
    
    def on_stop(self):
        
        
        
        GPIO.output(cilinder, 0)
        self.root_window.close()
        

    def build(self):
        return RootWidget()


if __name__ == '__main__':
    
    Window.fullscreen = 'auto'
    
    MIM().run()