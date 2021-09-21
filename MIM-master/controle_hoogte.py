#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 13 14:11:17 2021

@author: pi
"""

#Voltage1 = 40
#Voltage2 = 12
#Voltage3 = 0
#
#steps1 = -6
#steps2 = -4
#steps3= -2
#steps12 = (steps1^2)
#steps22 = (steps2^2)
#steps32 = (steps3^2)
#
#
##A1 = ((Voltage3-Voltage1)-((Voltage2-Voltage1)*((steps3-steps1)))/(steps2-steps1))
##A2 = ((steps32-steps12)-((steps3-steps1))/((steps2-steps1)*(steps22-steps12)))
#
#A= ((Voltage3-Voltage1)-(Voltage2-Voltage1)*(steps3-steps1)/(steps2-steps1))/((steps32-steps12)-(steps3-steps1)/(steps2-steps1)*steps22-steps12)
#
#B = ((Voltage2-Voltage1)-A*(steps22-steps12))/(steps2-steps1)
#
#
#StepsMin = -B/(2*A)
#C = Voltage1-(A*(steps12))-(B*steps1)
#
#
#print(A,B, C)
def coefficient(x,y):
    x_1 = x[0]
    x_2 = x[1]
    x_3 = x[2]
    y_1 = y[0]
    y_2 = y[1]
    y_3 = y[2]

    a = y_1/((x_1-x_2)*(x_1-x_3)) + y_2/((x_2-x_1)*(x_2-x_3)) + y_3/((x_3-x_1)*(x_3-x_2))

    b = (-y_1*(x_2+x_3)/((x_1-x_2)*(x_1-x_3))
         -y_2*(x_1+x_3)/((x_2-x_1)*(x_2-x_3))
         -y_3*(x_1+x_2)/((x_3-x_1)*(x_3-x_2)))

    c = (y_1*x_2*x_3/((x_1-x_2)*(x_1-x_3))
        +y_2*x_1*x_3/((x_2-x_1)*(x_2-x_3))
        +y_3*x_1*x_2/((x_3-x_1)*(x_3-x_2)))

    return a,b,c

x = [-6.-5,-4]
y = [40,24,12 ]

a,b,c = coefficient(x, y)
Xmin = -b/(2*a)

print ("a = ", a)
print ("b = ", b)
print ("c = ", c)
print("min = ", Xmin)