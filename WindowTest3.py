# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 09:34:30 2017

@author: Kingsley Baxter
"""

#Importing packages; tkinter is to build a GUI to make interaction easier; serial is used to interact with
#the I/O port to send data through
import tkinter                                         
import serial
import time
#Predefining a bunch of variables that are used later on to prevent error and speed up allocation
dataAZ = [0,0,0,0]
dataEL = [0,0,0,0]
NULL = chr(0)
Azimuth = 0.0
Elevation = 0.0

Root =    tkinter.Tk()
Az = tkinter.StringVar(Root)
Az.set("0.0")
El = tkinter.StringVar(Root)
El.set("0.0")
TarAZ = tkinter.StringVar(Root)
TarAZ.set("0.0")
TarEL = tkinter.StringVar(Root)
TarEL.set("0.0")
Already = tkinter.BooleanVar(Root)
Already.set(True)
#Defining and Opening the port used in the program. Only exiting the program through the GUI will close the Port.
Server = serial.Serial()
Server.port = 'COM3'
Server.baudrate = 460800
Server.open()
#The Rot2Prog protocol has three commands: Goto, Status, and Stop. Status and Stop don't require coordinate input
#So they can be defined now to improve efficiency in the program. See above for an explanation of the protocol.
Stop_String = "W" + NULL*10 + chr(15) + chr(32)
Stop_Command = Stop_String.encode('utf-8')
Read_String = "W"+NULL*10 + chr(31) + chr(32)
Read_Command = Read_String.encode('utf-8')

#The Stop function is the first one to be defined so that it can be inserted into future functions.
def Stop_Drive():
    Server.write(Stop_Command)
    
#The read function, it sends the command and then reads the response. See above for a detailed breakdown of the
#response.[Currently not working as intended]
def ReadFunction():
    Server.write(Read_Command)
    Data = Server.read(11).decode('utf-8')
    Bin = Server.read()
    DataAZ = Data[1:5]                              #The Azimuth is the 2nd through 5th character sent in the response
    DataEL = Data[6:10]                             #The Elevation is the 6th through 10th character sent in ther response
    for e in range(0,4):
        dataAZ[e] = ord(DataAZ[e])                  #converts the ascii character into a number since it uses ascii index 0-10 the number doesn't need to be manipulated further.
        dataEL[e] = ord(DataEL[e])
    Azimuth = ((dataAZ[0]*1000 + dataAZ[1]*100 + dataAZ[2]*10 + dataAZ[3])/10)-360
    Elevation = ((dataEL[0]*1000 + dataEL[1]*100 + dataEL[2]*10 + dataEL[3])/10)-360
    Azimuth = "{0:.1f}".format(Azimuth)
    Elevation = "{0:.1f}".format(Elevation)
    Az.set(Azimuth)
    El.set(Elevation)
    if Already.get() == False:
        BetaSet_Drive()
    
    Root.after(500, ReadFunction)                 #Returns the two numbers so they can be displayed.

#Important function. Can't predefine the command since it changes with the coordinates. Will set an Azimuth and
#Elevation for the Drive to point at.
def BetaSet_Drive():
    Target = float(TarAZ.get())
    Current = float(Az.get())
    Comparison = Target - Current
    if abs(Comparison) > 180:
        return
     
    AZ = Target
    AZ = AZ + 360
    AZ = str(AZ)                           #Its easier to split up a string then a number, at least to my knowledge.
    if len(AZ) < 5:
        AZ = (5 -len(AZ))*"0" + AZ
    AZhundreds = AZ[0]                                                                 #Seperates the Digits out so that they can be read into their own byte.
    AZtens =     AZ[1]
    AZdigits =   AZ[2]
    AZtenths =   AZ[4]
    
    EL  = float(TarEL.get()) + 360
    EL = str(EL)                           #Its easier to split up a string then a number, at least to my knowledge.
    if len(EL) < 5:
        EL = (5 -len(EL))*"0" + AZ
    ELhundreds = AZ[0]                                                                 #Seperates the Digits out so that they can be read into their own byte.
    ELtens =     AZ[1]
    ELdigits =   AZ[2]
    ELtenths =   AZ[4]
    
    
    ACC = chr(10)                                                                      #The Accuracy of this driver is 0.1 Degrees Therefore to change the numbers from integers to floats a quotient of 10 is required.
    COMMAND = chr(47)                                                                  #Command 47 is the Set command, there are two others Read (31) and Stop (15).
    END = chr(32)                                                                      #The End of the transmission is marked by a space bar or ascii character 32.
    
    Set_String = "W" + AZhundreds + AZtens + AZdigits + AZtenths + ACC + ELhundreds + ELtens + ELdigits + ELtenths + ACC + COMMAND + END  #The culmination of the processes above are fed into this string.
    Set_Command = Set_String.encode('utf-8')     #Which is then encoded into byte information to be sent.
    Server.write(Stop_Command)
    time.sleep(0.1)
    Server.write(Set_Command)
    Already.set(True)

def Error_Range():    
    Error = tkinter.Toplevel()
    Error.title("Oops, Something went Wrong!")
    message = tkinter.Label(Error, text="Only Azimuths and Elevations between -360 and 360 are allowed. Please choose a different the number.")
    returnbutton = tkinter.Button(Error, text="Will do", command=Error.destroy)
    message.pack()
    returnbutton.pack()

def Error_bar():    
    Error = tkinter.Toplevel()
    Error.title("Oops, Something went Wrong!")
    message = tkinter.Label(Error, text="An Entry was invalid, Please try again only using numbers and periods")
    returnbutton = tkinter.Button(Error, text="Will do", command=Error.destroy)
    message.pack()
    returnbutton.pack()


def Set_Drive(AZInput, ELInput):
    BREAK = float(Az.get())+179
    BREAK2 = float(Az.get())-179
    try:
        AZ = float(AZInput)                     #Converts the string to a Float for numerical manipulation
        EL = float(ELInput)
    except ValueError:
        Error_bar()
        return

    if (EL < -0) or (EL > 90):
        Error_Range()
        return
    
    if (AZ < 0) or (AZ > 360):
        Error_Range()
        return
    TarAZ.set(str(AZ))
    TarEL.set(str(EL))
    
    if AZ > BREAK:
        AZ = BREAK
        Already.set(False)
    elif AZ < BREAK2:
        AZ = BREAK2
        Already.set(False)
        #The controller can't take negative number so all number are increased by 360 degrees


    EL = EL + 360
    AZ = AZ + 360
    AZ = str(AZ)                           #Its easier to split up a string then a number, at least to my knowledge.
    if len(AZ) < 5:
        AZ = (5 -len(AZ))*"0" + AZ
    EL = str(EL)
    if len(EL) < 5:
        EL = (5 -len(EL))*"0" + AZ
    
    AZhundreds = AZ[0]                                                                 #Seperates the Digits out so that they can be read into their own byte.
    AZtens =     AZ[1]
    AZdigits =   AZ[2]
    AZtenths =   AZ[4]

    ELhundreds = EL[0]                                                                 #Same for Elevation as Azimuth
    ELtens =     EL[1]
    ELdigits =   EL[2]
    ELtenths =   EL[4]
    
    ACC = chr(10)                                                                      #The Accuracy of this driver is 0.1 Degrees Therefore to change the numbers from integers to floats a quotient of 10 is required.
    COMMAND = chr(47)                                                                  #Command 47 is the Set command, there are two others Read (31) and Stop (15).
    END = chr(32)                                                                      #The End of the transmission is marked by a space bar or ascii character 32.

    Set_String = "W" + AZhundreds + AZtens + AZdigits + AZtenths + ACC + ELhundreds + ELtens + ELdigits + ELtenths + ACC + COMMAND + END  #The culmination of the processes above are fed into this string.
    Set_Command = Set_String.encode('utf-8')     #Which is then encoded into byte information to be sent.
    
    Server.write(Set_Command)
            
    
 #Used to exit the program, has the benefit of closing the port as well so other programs can use it. Now attached to the protocol of closing the window itself. 
def End_Drive():
    Stop_Drive()
    Server.close()
    Root.destroy()

#Defining all the GUI elements. 

Root.title("Drive Monitor")
Stop =    tkinter.Button(Root, text="Stop the Drive", pady=5, command= lambda: Stop_Drive())
AZEntry = tkinter.Label(Root, text="Please enter a new Azimuth below")
ELEntry = tkinter.Label(Root, text="Please enter a new Elevation below")    
AZLabel = tkinter.Label(Root, textvariable=Az)
ELLabel = tkinter.Label(Root, textvariable=El)
ExtraAZ = tkinter.Label(Root, text="The current Azimuth is ")
ExtraEL = tkinter.Label(Root, text="The current Elevation is ")
TARGET1 = tkinter.Label(Root, text="The Target Azimuth is ")
TARGET2 = tkinter.Label(Root, text="The Target Elevation is ")
AZTARGET = tkinter.Label(Root, textvariable=TarAZ)
ELTARGET = tkinter.Label(Root, textvariable=TarEL)
AZBox =   tkinter.Entry(Root)
AZBox.insert(10,"000.0")
ELBox =   tkinter.Entry(Root)
ELBox.insert(10,"000.0")
Alred =   tkinter.Label(Root, textvariable=Already)
Set =     tkinter.Button(Root, text="Set Drive to above coordinates", command= lambda: Set_Drive(AZBox.get(), ELBox.get()))
End =     tkinter.Button(Root, text="Exit Program", command=lambda: End_Drive())

#Placing all the widgets into the Root window using the grid placement method.


Stop.grid(row=0, column=2)
AZEntry.grid(row=1, column=0)
AZBox.grid(row=2, column=0)
ELEntry.grid(row=3, column=0)
ELBox.grid(row=4, column=0)
AZLabel.grid(row=2, column=5)
ELLabel.grid(row=3, column=5)
ExtraAZ.grid(row=2, column=4)
ExtraEL.grid(row=3, column=4)
TARGET1.grid(row=0, column=4)
TARGET2.grid(row=1, column=4)
AZTARGET.grid(row=0, column=5)
ELTARGET.grid(row=1, column=5)
Set.grid(row=5,column=0)
End.grid(row=5, column=4)
Alred.grid(row=5, column=3)

Root.wm_protocol("WM_DELETE_WINDOW", End_Drive)
Root.after(500, ReadFunction)

Root.mainloop()
