#Read from arduino and pi-cam and save to database

#----------------------------------------------------Libraries-----------------------------------------------------------------------------------------------------------------------

#need this to access Arduino's serial port
import serial 

#library for having different filenames for the pi-cam images
import time 

import mysql.connector 

#library for using the pi-cam
from picamera import PiCamera 

#library to add delay
from time import sleep 

#-----------------------------------------------------Necessary initializations---------------------------------------------------------------------------------------------------

#/dev/ttyACM0 is the serial monitor which have the arduino readings - must match the serial monitor in the arduino console
arduino = serial.Serial("/dev/ttyACM0") 

#same baudrate as defined in the arduino code
arduino.baudrate = 9600

#to enable the pi-cam
camera = PiCamera()

#to get the image in the correct orientation
camera.rotation = 180

#camera.start_preview() 

#------------------------------------------------------Loop to read from arduino and pi-cam and place in database-----------------------------------------------------

#for loop - continuous loop which will be running as long as the pi-cam continues to take photos
#all the pictures are saved in a unique filename which is defined by the hour, minute and second
for filename in camera.capture_continuous('img{timestamp:%H-%M-%S}.jpg'):
	
    #the filepath is defined to be in the desktop (the images are stored in the desktop as default as the python script is saved and ran from the desktop directory)
    filepath = '/home/pi/Desktop/%s' %filename

    #delay of 8 seconds (this was set inaccordance to the delay of the waypoints when the rover was moving)
    sleep(8) 

    #read line from the serial port of the arduino
    data = arduino.readline()

    #split the data when a "tab (\t)" is seen
    #pieces is now an array of data
    pieces = data.split("\t")

    #instances of the array "pieces" is stored in different variables
    Direct_Irradiance = pieces[0]
    Indirect_Irradiance = pieces[1]
    
    #"mysql.connector" is a Python driver for connecting with MySQL servers and access MySQL databases
    #I recommend using the same user, password and host. The database can be changed.
    #the database and table inside the database must be created beforehand for this to work
    con = mysql.connector.connect(user='root', password='dewa123', host='localhost', database='test');

    #a cursor allows you to iterate a set of rows returned by a query and process each row individually
    cursor = con.cursor()
    
    #SQL insert statement which inserts into three different columns into the table called "Irradiance_Values" row by row
    cursor.execute("INSERT INTO Irradiance_Values (Direct_Irradiance, Indirect_Irradiance, Image_Path) VALUES (%s, %s, %s)", (pieces[0],pieces[1], filepath))

    #printing the filepath after the SQL statement is executed to ensure the data was added to the database
    print(filepath)
    
    #close the connection to the database 
    con.commit()
    cursor.close()


