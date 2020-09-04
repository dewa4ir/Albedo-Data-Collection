#Read from arduino and save to database

#----------------------------------------------------Libraries-----------------------------------------------------------------------------------------------------------------------

#need this to access Arduino's serial port
import serial 

#library for having different filenames for the pi-cam images
import time 

#library to connect to the mySQL server
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

#------------------------------------------------------Loop to read from arduino and place in database-------------------------------------------------------------------

#while true loop - continuous loop which will be running as long as the pi-cam continues to take photos
#all the pictures are saved in a unique filename which is defined by the hour, minute and second
while True:

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
    
    #SQL insert statement which inserts into two different columns into the table called "Irradiance_Values" row by row
    #I recommend making a brand new table and database
    cursor.execute("INSERT INTO Irradiance_Values (Direct_Irradiance, Indirect_Irradiance) VALUES (%s, %s)", (pieces[0],pieces[1]))
    
    #close the connection to the database 
    con.commit()
    cursor.close()


