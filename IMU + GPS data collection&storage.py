#data type = dictionary
#dictionary has keys and values that map to the specific keys

#-----------------------------------------------------------------------------Libraries-------------------------------------------------------------------
#library to add delay in the code
import time
#library to add randomization
import random
#library to get date & time for unique csv filenames
from datetime import datetime
#python implementation of mavlink protocol
from pymavlink import mavutil
#library to connect python with MySQL
import mysql.connector

#----------------------------------------------------------------------------Necessary initializations-------------------------------------------------

#global variable that gets updated by different methods
current_file_name = None

#----------------------------------------------------------------------------Methods---------------------------------------------------------------------
# https://gist.github.com/vo/9331349

#method to store the message (type = dictionary) from the pixhawk
def msg_store(msg):
  #extract the values from the message dictionary and place in a list
  msg_vals = list(msg.values())
  #append the data to the current file
  with open(current_file_name, "a") as output:
    output.write(','.join(str(v) for v in msg_vals) + "\n")
  #return the method call
  return

#method to store the msg key (msg type = dictionary); new_file_flag is flag (1 or 0)
def msg_key_store(msg,new_file_flag):
  #if the flag is 1, then execute the following if statement
  if(new_file_flag):
    #extract the keys from the msg (dictionary) and store in a list format
    msg_vals = list(msg.keys())
    # current date and time
    now = datetime.now() 
    #need this statement to access the global variable inside the method
    global current_file_name
    #update the global variable with a filename (csv file) that contains the current date & time
    current_file_name = "imu"+now.strftime("%Y.%m.%d-%H-%M-%S")+".csv"
    #append the data to the current file
    with open(current_file_name, "a") as output:
      output.write(','.join(str(v) for v in msg_vals) + "\n")
    #print statement shown on the terminal running the python code
    print("New file name: %s" % current_file_name)
    #return the method call
    return

  #if the flag is 0, then pass
  else:
    pass

  #return the method call
  return 

#method to read IMU data 
#arguments: master - contains the mavlink connection; new_file_flag is flag (1 or 0)
def readIMU_loop(master,new_file_flag):

    #for loop that loops until the range starting from 0 till the number specified within the range
    for x in range(1): #I have used 1 here for simulation purpose - but you can increase this value if you think message will take longer to be received - you have to estimate - so play around with the range(1) to a different range
        #extracts the RAW_IMU data from the pixhawk using mavlink
        msg = master.recv_match(type='RAW_IMU', blocking=False)
        # break loop once most recent messages have updated dict
        # if msg is not null, execute the if statements
        if msg is not None:
            #store the extracted data as dictionary datatype
            message = msg.to_dict()
            msg_key_store(message,new_file_flag) #method call
            msg_store(message) #method call
            return 0 #timeout_flag = 0
        elif (x == 0): #Important: Whatever range you pick above make sure this value is -1 of that - for example I picked 1 above so here it is 0
            return 1 #timeout_flag = 1

#method to read GPS data 
#arguments: master - contains the mavlink connection
def readGPS_loop(master):
    
    myDict = {} #dictionary object

    #"mysql.connector" is a Python driver for connecting with MySQL servers and access MySQL databases
    #I recommend using the same user, password and host. The database can be changed.
    #the database and table inside the database must be created beforehand for this to work
    con = mysql.connector.connect(user='root', password='dewa123', host='localhost', database='test');

    #for loop that loops until the range starting from 0 till the number specified within the range
    for x in range(1): #I have used 1 here for simulation purpose - but you can increase this value if you think message will take longer to be received - you have to estimate - so play around with the range(1) to a different range
        #extracts the GLOBAL_POSITION_INT (GPS) data from the pixhawk using mavlink
        msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=False)

        # break loop once most recent messages have updated dict
        # if msg is not null, execute the if statements
        if msg is not None:
            #store the extracted data (msg) as dictionary datatype
            myDict = msg.to_dict()

            #the following statements are to needed to store the GPS data in a table in the database
            #ensure a table is already created in the database with the column names as keys and they are in the same order as seen when the GPS data is printed
            placeholders = ', '.join(['%s'] * len(myDict))
            columns = ', '.join(myDict.keys())
            #sql statement: GPS - table name
            sql = "INSERT INTO GPS ( %s ) VALUES ( %s )" % (columns, placeholders)
            #a cursor allows you to iterate a set of rows returned by a query and process each row individually
            cursor = con.cursor()
            cursor.execute(sql, list(myDict.values())) #execute the sql statement and use the list with the dictionary values
            #close the connection to the database
            con.commit()
            cursor.close()
            return 0 #timeout_flag = 0
            
        elif (x == 0): #Important: Whatever range you pick above make sure this value is -1 of that - for example I picked 1 above so here it is 0
            return 1 #timeout_flag = 1

#method
def msg_loop():
    master = connect_mav() #method call returns mavlink connection

    #initialization
    new_file_flag = 1
    timeout_flag = 0

    #print statements
    print("TIMEOUT FLAG:")
    print("0 means mavlink connection EXIST and timeout didn't occur")
    print("1 means mavlink connection LOST and timeout occured")
    print("\n\n\n")

    #loop
    while True:
        timeout_flag = readIMU_loop(master, new_file_flag) #method call
        #print statement
        print("TIMEOUT FLAG: %s" % timeout_flag)
        #set timeout_flag as 0 or 1 based on the OR statement
        timeout_flag = readGPS_loop(master) | timeout_flag 

        new_file_flag = 0

        #execute if statement if timeout_flag = 1 
        if (timeout_flag):
            master = connect_mav() #method call returns mavlink connection
            new_file_flag = 1

        #delay
        time.sleep(3)

#method to connect to pixhawk using mavlink
def connect_mav():
    #print statement shown on the terminal running the script
    print("connecting mavlink")

    #mavlink connection using the port and baudrate
    master = mavutil.mavlink_connection("/dev/serial0", baud = 921600)

    #this ensures whether the connection is established or not
    master.wait_heartbeat()

    #requesting data from the parameters set in mission planner for pixhawk
    master.mav.request_data_stream_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_RAW_SENSORS,    # stream id
        1,                                      # message rate hertz
        1                                       # 1 start, 0 stop
    )

    #return method call
    return master

#start method called msg_loop()
msg_loop()