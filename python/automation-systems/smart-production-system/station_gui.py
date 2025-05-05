#lines needing changes:
# line with post_data change llgs001 hostname in the string in the server function
# line with :  with open('Data/New_Document_texte_next_step.txt', 'r')as file: put 

#!/usr/bin/python3
import os 
import re 
import tkinter as tk 
from tkinter import * 
from tkinter import messagebox,Tk, Frame, Label, Scrollbar, Canvas 
import requests
#import RPi.GPIO as GPIO
import signal
import time
import socket
import datetime as datetime
import paho.mqtt.client as mqtt
import sqlite3
import matplotlib.pyplot as plt

#GPIO Configuration 
forward_relay=16
end_relay= 20

#counter is used here to count how many collections are created by the worker
global counter
counter = 0

'''
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(forward_relay, GPIO.OUT)
GPIO.setup(end_relay, GPIO.OUT)
'''

                                                 #################################################
def read_txt_file():
    #txt file reading
    #with open('/home/pi/LLGS/txt_configuration.txt', 'r')as file:
    with open('C:/Users/ab/Desktop/N02/LLGS.txt', 'r')as file:
        content = file.read()

    # Define regular expression pattern to extract the needed strings
    pattern = r'unique_splices:(.*?)module_list:(.*?)unique_wires:(.*?)wires_code:(.*?)$'

    # Find the match in the content
    match = re.search(pattern, content, re.DOTALL)  # Added re.DOTALL to match across lines

    # Extract the needed strings into data lists used in the programming of the structure data 
    if match:
        UNIQUE_SPLICES = [splice.strip('"') for splice in match.group(1).split(',')]
        module_list_qr = [splice.strip('"') for splice in match.group(2).split(',')]    
        UNIQUE_WIRES = [splice.strip('"') for splice in match.group(3).split(',')]  
        Unique_QR_Codes_wires = [splice.strip('"') for splice in match.group(4).split(',')] 
        #print("UNIQUE_SPLICES",UNIQUE_SPLICES)
        #print('module_list_qr', module_list_qr)
        #print('UNIQUE_WIRES:')
        #print('Unique_QR_Codes_wires:')
        #the qr dictionnary stores module_list qr: wire qr
        QR_dict = dict(zip(module_list_qr, Unique_QR_Codes_wires))

        #the bar dictionnary stores bar codes: "QR_dict"
        BAR_dict = dict(zip(UNIQUE_SPLICES,module_list_qr))

        return UNIQUE_WIRES, QR_dict, BAR_dict
    else:
        msg=messagebox.showinfo("Configuration File Problem",message="problem with configuration file loaded.")
        print("problem with configuration file loaded. use print(content) in code after pattern.")

class ProductionDatabase:
    def __init__(self, db_file="logs.db"):
        self.db_file = db_file
        if not os.path.exists(db_file):
            self.create_database()

    def create_database(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE production
                     ( day TEXT,
                     time TEXT,
                     workstation TEXT,
                     shift INTEGER,
                     splice TEXT,
                     batch INTEGER,
                     code TEXT 
                     )''')
        conn.commit()
        conn.close()

    def write_data_sqlite(self, reference_name, batch_quantity, qr_sent):
        # Determine shift based on time of day
        hour = datetime.datetime.now().hour
        # Determine current shift
        if 0 <= hour < 8:
            shift = 1
        elif 8 <= hour < 16:
            shift = 2
        else:
            shift = 3
        print (shift)
        # Get timestamp in HH:MM format
        timestamp = datetime.datetime.now().strftime("%H:%M")

        # Get machine name N02G2D215
        machine_hostname = socket.gethostname()
    
        machine_name="N"+machine_hostname[-2:]
        #print(datetime.datetime.now().strftime("%Y-%m-%d"), timestamp, shift, reference_name, batch_quantity, qr_sent, machine_name)
        # Insert data into the production table
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute('''INSERT INTO production
                 (day, time, workstation, shift, splice, batch, code)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (datetime.datetime.now().strftime("%Y-%m-%d"), timestamp, machine_name, shift, reference_name, batch_quantity, qr_sent))
        conn.commit()
        conn.close()

class Table:
    def __init__(self, window, data):
        self.root = window
        body=window_header("data table")
        # Create a frame to hold the canvas and scrollbar
        frame = Frame(body)
        frame.pack(side="top", fill='both', expand=True)

        # Create a canvas to hold the table
        canvas = Canvas(frame)
        canvas.pack(side="left", fill='both', expand=True)

        # Create a vertical scrollbar
        scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Create a frame to hold the table data
        table_frame = Frame(canvas)
        canvas.create_window((0, 0), window=table_frame, anchor="nw")

        headers = ["Date", "Time", "Workstation", "Shift", "Splice Name", "Batch", "Code Sent"]

        # Create table headers
        for j, header in enumerate(headers):
            padx = 10
            if j == len(headers) - 1:
                padx = 100
            lbl = Label(table_frame, text=header, font=('Arial', 16, 'bold'), borderwidth=1, relief="solid", padx=padx)
            lbl.grid(row=0, column=j, sticky="nsew")

        # Insert data into the table
        for i, row in enumerate(data):
            for j, item in enumerate(row):
                padx = 10
                if j == len(data) - 1:
                    padx = 100
                if window.winfo_screenwidth() > 1400:
                    wrap = 1000
                elif window.winfo_screenwidth() > 1800:
                    wrap = 1500
                else:
                    wrap = 2000
                lbl = Label(table_frame, text=item, font=('Arial', 12), borderwidth=1, relief="solid", wraplength=wrap, padx=padx)
                lbl.grid(row=i + 1, column=j, sticky="nsew")

        # Configure the canvas to use the scrollbar
        canvas.config(yscrollcommand=scrollbar.set)

        # Update the scroll region
        table_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # bottom section
        bottom_section = Frame(window, height=70, bg="white")
        bottom_section.pack(side=tk.BOTTOM, fill=tk.X)
        # Button Example
        button_function(bottom_section, "Back", lambda: start_page(wire_name="", mode="feeding"), 0.5, 0.5, yellow_color)

def plot():
    # Connect to the SQLite database
    conn = sqlite3.connect('logs.db')
    cursor = conn.cursor()

    #production(day TEXT, time TEXT, workstation TEXT, shift INTEGER, splice TEXT, batch INTEGER, code TEXT)
    
    # Fetch data from the database
    cursor.execute("SELECT day, COUNT(splice) FROM production GROUP BY day")
    data = cursor.fetchall()        

    # Close the connection
    conn.close()

    # Process data for plotting
    dates = [item[0] for item in data]
    scan_counts = [item[1] for item in data]

    # Plotting the bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(dates, scan_counts, color='blue')
    plt.xlabel('Date')
    plt.ylabel('Number of Scans')
    plt.title('Number of Scans per Day')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def fetch_data_from_db(db_file, table_name):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute(f"SELECT * FROM {table_name}")
    rows = c.fetchall()
    conn.close()
    return rows

class create_daily_file:
    def __init__(self):
        # Get current date
        now = datetime.datetime.now()
        day = now.strftime("%A")  # Get day of the week
        date = now.strftime("%d-%m-%Y")  # Get date in YYYY-MM-DD format
        # Get hostname
        hostname = socket.gethostname()

        # Define folder name and file name
        self.folder_name = "LLGS Logs"
        self.file_name = f"LLGS_{hostname}_{date}.txt"

        # Define full file path
        self.full_file_path = os.path.join(os.getcwd(), self.folder_name, self.file_name)

        # Check if folder exists, if not, create it
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)
            print(f"Folder '{self.folder_name}' created.")

        # Check if file already exists
        if os.path.exists(self.full_file_path):
            print(f"File '{self.full_file_path}' already exists.")
        else:
            # Create and write to the file
            with open(self.full_file_path, 'w') as file:
                file.write(f"This is {day}, {date}.\nShift-Time-Reference-Quantity\n")

            print(f"File '{self.full_file_path}' created.")
    
    
    def write_data(self, ref, quantity):
        # Get current time
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute

        # Determine current shift
        if 0 <= hour < 8:
            shift = "Shift_1"
        elif 8 <= hour < 16:
            shift = "Shift_2"
        else:
            shift = "Shift_3"

        # Open file in read mode to read existing content
        with open(self.full_file_path, 'a') as file:
            file.write(f"{shift}-{hour:02d}:{minute:02d}-{ref}-{quantity}\n")

#the decode_qr_code function is not used here, when we have image as entry it will be used N02GD215A N02G2D216.03

def kill_script():
    #control_combo_end(end_relay)
    os.kill(os.getpid(), signal.SIGTERM)

# Function to assign the entry box text to qr_var
def assign_qr(ent_box):
    qr_text = ent_box.get()
    qr_var.set(qr_text)  # Set qr_var to the entered text

#start_processing is called when the start button is pressed, it opens the scond page and checks for empty entry
def start_processing(qr_var, mode="production"): 
    if qr_var.get():
        clear_window()
        main(qr_var.get(),mode)
    else:
        show_error_message("Please enter QR code")

def mqtt_message(message):
    try:
        # MQTT broker address and port
        broker_address = "192.168.16.50"
        port = 1883  # Default MQTT port

        # Connect to the MQTT broker
        client = mqtt.Client()
        client.connect(broker_address, port)

        # Get hostname
        hostname = socket.gethostname()

        # Format message
        msg = f"{hostname}@{message}"
        
        # Publish message to a topic
        # Publish message to the specified topic
        topic = "LLGS"
        client.publish(topic, msg)

        # Disconnect from the broker
        client.disconnect()
        print("Message: ",msg," ,published successfully to ",topic)
    except Exception as e:
        print(f"An error occurred: {e}")
        if message=="end":
            messagebox.showerror("MQTT connection Error", "could not establish connection with raspberry LLGS0, the message was the end message.")
        else:
            messagebox.showerror("MQTT connection Error", "could not establish connection with raspberry LLGS0, the message was the new scan.")

def server(qr_data, mode=""):
    hostname = socket.gethostname()
    if hostname:
        try:
            # Change the hostname here (raspberry pi name)
            post_data = "HostName=llgs001&ScanText=" + str(qr_data)
            
            # Replace "http://10.50.33.27/llgswebservice/scanner.asmx/NewScan" with the IP address of your server (PC2)
            server_url = "http://10.50.33.27/llgswebservice/scanner.asmx/NewScan"
            
            # Prepare the request headers
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            
            # Send the data to the server with a timeout of 5 seconds
            response = requests.post(server_url, headers=headers, data=post_data, timeout=5)
            
            # Check if the request was successful
            if response.status_code == 200:
                if mode=="test":
                    messagebox.showinfo("NEGATIF TEST",message=f"Negatif test finished.")
                else:
                    print("Data sent successfully!")
                    messagebox.showinfo("Success", "Data sent successfully!")
                
            else:
                if not mode=="test":
                    print("Error sending data to the server. Response:", response.text)
                    messagebox.showerror("Server Error", "Error sending data to the server.")
                
        except requests.exceptions.Timeout:
            if mode=="test":
                messagebox.showinfo("NEGATIF TEST",message=f"Negatif test failed to reach server.") 
            else:
                print("Request timed out. Please check your network connection.")
                messagebox.showerror("Server Connection Error","Could not establish connection with server.")
                
        except requests.exceptions.RequestException as e:
            if mode=="test":
                messagebox.showinfo("NEGATIF TEST",message=f"Negatif test failed, An error occurred: \n{e}", ) 
            else:
                print("An error occurred:", e)
                messagebox.showerror("Error", f"An error occurred: {e}")

#send a 5v signal to the combo followed by low to it's end button
'''
def control_combo_end(combo_led):
    GPIO.output(combo_led, GPIO.HIGH)
    time.sleep(0.7)
    GPIO.output(combo_led, GPIO.LOW)
'''
#for our case what matters to us is the second to last element in the qr data, if the qr only has 1 @
# then the format doesn't have the 1 and x --> on and off wires
def process_qr(qr_text):
    #"LJS@000000001@001@I3R@LOT@50@.@20240416220616@.@.@.@IP RH L663@0.0000@G2D215@111xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx@000000001="
    #put wires (1,0) in index 0, 1 and quantity in index 1, ref in index 2

    qr_parts = qr_text.split('@')
    #asseign the data used from the wire qr to the qr parts array
    if len(qr_parts) >= 2 :
        data=[qr_parts[-2],qr_parts[-11],qr_parts[-3]]
        return data
    else:
        print("Invalid QR code format")
        return None

#used in the process_qr --> can be deleted and replaced with one line, this only shortens the code written
def show_error_message(message):
    messagebox.showerror("Empty Field",message=message) 

#here is the top section layout and body color along with title of the page
def window_header(page_title):
    window.attributes('-fullscreen', True)
   
    # Top section
    top_section = Frame(window, height=60, bg="#D5D5D5")
    top_section.pack(side=tk.TOP, fill=tk.X)
    
    # Titles
    label_function(page_title, 0.5, 0.5,top_section)
    label_function("LLGS", 0.95, 0.5, top_section)

    # Load and resize the image
    img = tk.PhotoImage(file="C:/Users/ab/Desktop/Raspberry_PI/Programming/Final_Code/LLGS_working_version/images/Lear.png")
    #resize image
    width, height = 145, 45
    img = img.subsample(img.width() // width, img.height() // height)  
    image_label = tk.Label(top_section, image=img, bg="#D5D5D5")
    image_label.image = img  # Keep a reference to avoid garbage collection
    image_label.place(relx=0.01, rely=0.5, anchor="w")
    
    body = tk.Canvas(window, bg="white", width=window.winfo_screenwidth(), height=window.winfo_screenheight() - 60)
    body.pack(fill=tk.BOTH, expand=True)  # Use fill=tk.BOTH and expand=True to make it fill the remaining space
    return body

#draw the wire shape
def display_wire_shape(canvas, offsety, black_x1, black_x2, yellow1_x1, yellow1_x2, yellow2_x1, yellow2_x2, black_width,yellow_width):
    y_coordinate =  2+offsety
    points = [(black_x1,  y_coordinate), (black_x2,  y_coordinate)]
    yellow1 = [(yellow1_x1,  y_coordinate), (yellow1_x2,  y_coordinate)]
    yellow2 = [(yellow2_x1,  y_coordinate), (yellow2_x2,  y_coordinate)]
    # Draw the wire-like shape on the canvas
    canvas.create_line(points, fill="black", width=black_width)
    canvas.create_line(yellow1, fill="#B8860B", width=yellow_width)
    canvas.create_line(yellow2, fill="#B8860B", width=yellow_width)

#displays the wire id for each one
def display_wire_ID(canvas, id,center_x,offsety, value=False):
    offsety=offsety-15
    if value==False:
        canvas.create_text(center_x,offsety, text=id, font=("Arial bold", 18), fill="black")
    else:
        canvas.create_text(center_x,offsety, text=id, font=("Arial bold", 18), fill="black")

def button_function(instance, name, action, relx, rely, color):

    button = Button(instance, width=14, text=name, command=action, font=("Helvetica", 24, "bold"), background="white", bg=color)
    button.place(relx=relx, rely=rely, anchor=CENTER)

def label_function(name, relx, rely, root, bg="#D5D5D5", size=28):
# excel path label
    scan_text = Label(root, text=name, font=("Helvetica", size, "bold"), bg=bg)
    scan_text.place(relx=relx, rely=rely, anchor="center")
    
def entry_function(text_variable, relx, rely):
    entry_box = Entry(window, textvariable=text_variable, width=100, font=("Arial", 12),  background="#D5D5D5",justify="center")
    entry_box.place(relx=relx, rely=rely, anchor="center")
    return entry_box

#display wire information and progress, default as yellow for progress box
def wire_information_progress(canvas, progress_color="#ECEC4C"):
    #screen dimensions
    screenwidth=window.winfo_screenwidth()
    box_x1=screenwidth-300
    
    canvas.delete("txt_main")
    canvas.delete("txt")
    
    #reference name and number if wires
    canvas.create_rectangle(box_x1-100, 30, box_x1+250, 180, fill="white")
    canvas.create_text(box_x1+75, 100, text=f"Splice name: {ref}\n\nNumber of wires: {number_wires}", font=('Arial', 22,'bold'), fill="black", tags="txt_main")
    #progress of finished wires
    canvas.create_rectangle(box_x1-100, 200, box_x1+250, 250, fill=progress_color)
    canvas.create_text(box_x1+75, 225, text=f"Finished: {counter}/{quantity}", font=('Arial', 24,'bold'), fill="black", tags="txt_main")

# Function to update the counter and label text
def increase_counter(canvas,modulelist_qr):
    global counter
    counter += 1
    
    #handles finished progress, green label and return to scan page
    if (counter)==quantity:
            #display wire information and progress
            wire_information_progress(canvas, progress_color="#33cc33")
            #display messagebox here
            msg=messagebox.showinfo("Production Finished",message=f"{counter} combinations are assembled.") 
            if msg:
                print("Combination completed successfully")
                #control_combo_end(end_relay)
                counter=1
                start_page()
                mqtt_message("end") 
                    
            
    #handles last forward, sends two server requests
    else:
        #print('FORWARD clicked')
        #display wire information and progress
        wire_information_progress(canvas)

#add this function when you have a decrease counter button
def decrease_counter(canvas):
    global counter
    counter -= 1
    #display wire information and progress
    wire_information_progress(canvas)

#empties the tkinter window from widgets 
def clear_window():
    # Iterate through all the widgets in the window and destroy them
    for widget in window.winfo_children():
        widget.destroy()

blue_color="#1373CE"
green_color="#21DC5F"
gray_color="#C4C4C4"
yellow_color="#FEFD41"

####################################### Second Page #######################################
#test with these wires preceded with N02 for the case of structure N02  GD216SX  |  N02G2D215
def back():
    start_page()
    mqtt_message("end")

def show_table_data():
    clear_window()
    # SQLite database file and table name
    db_file = "logs.db"
    table_name = "production"
    if not os.path.exists(db_file):
        print('no database')
        messagebox.showerror("warning","the database is unreachable")
    #use the fetch function to get data from the logs file
    data_from_db = fetch_data_from_db(db_file, table_name)
    # Create table and display data
    t = Table(window,data_from_db)

def main(bar_code,mode="production"):
    
    #delete spaces from the bar_code string begining and ending
    bar_code= bar_code.strip()
    
    #get the splice name from the bar code --> example:  N02G2D215 --> G2D215 delete the first 3 characters
    bar_splice= bar_code[3:]
    if bar_splice in BAR_dict:
        
        if mode=="production":
            #Get the module_list qr from the bar code 
            module_qr=BAR_dict[str(bar_splice)]
            #print("Reference QR:", module_qr)
            
            #get the wire qr code from the module list qr code
            wires_qr = QR_dict[str(module_qr)]

            #get the wires qr
            qr_data = process_qr(wires_qr)
            wires=qr_data[0]

            global ref 
            ref=qr_data[2]
    
            global quantity
            quantity=int(qr_data[1])
            #test
            #quantity=3
            ids = UNIQUE_WIRES
    
            global number_wires
            number_wires = 0
            for wire in wires: 
                if wire == "1":    
                    number_wires += 1
        
            #variables for the wire and ids display
            j = 0
            l=0
            k=0
            reset=0
            comb_dict = {} 
            for id_value, wire_value_str in zip(ids, wires):
                wire_value = wire_value_str.strip()  # Convert wire value to an integer
                comb_dict[id_value] = wire_value

            canvas=window_header("Wire Combination")

            # display the wire-like shape and adjust position according to the number of wires
            for key, value in comb_dict.items():
                plus=2
                w=17
                if screen_height>1300:
                    w=23
                    plus=4
                    
                if number_wires <= 20:
                    center=window.winfo_screenwidth()/2
                    if value == "1":
                        j += plus
                        offset = 3 + j * w  # Adjusting the offset for each wire
    
                        display_wire_ID(canvas, key,center, offset)
                        display_wire_shape(canvas, offset, center-250, center+250, center-275, center-250, center+250, center+275, 8, 4)
                elif number_wires > 20:
                    if value == "1":
                        reset += 1
                        if reset>20:
                            l+=plus
                            offset = 3 + l * w
                            center=window.winfo_screenwidth()/4 +450
                            display_wire_ID(canvas, key,center, offset,value=True)
                            display_wire_shape(canvas, offset, center-225, center+225, center-250, center-225, center+225, center+250, 8, 4)
                        else:
                            k+=plus
                            offset = 3 + k * w
                            center=window.winfo_screenwidth()/4 -100
                            display_wire_ID(canvas, key,center, offset,value=True)
                            display_wire_shape(canvas, offset, center-225, center+225, center-250, center-225, center+225, center+250, 8, 4)

            wire_information_progress(canvas)
            # forward button
            button_function(canvas, "Forward", lambda :increase_counter(canvas,str(module_qr)) if counter < quantity else None, 0.3, 0.92, green_color)
            # back button
            button_function(canvas,"BACK", lambda: back(), 0.7, 0.92, blue_color) 
            
            #database_update
            #print(ref,"\n",quantity,"\n",module_qr)
            production_database.write_data_sqlite(ref, quantity, module_qr)
            #server message
            print(module_qr)
            server(module_qr)
            #mqtt_message
            mqtt_message(bar_code[3:])
        else: 
            messagebox.showerror("Invalid Scan",f"you have scanned a wire bar code instead of the splice bar code\n{bar_code[3:]}")
            start_page("","feeding")
        
    elif ('T' + bar_splice[1:]) in BAR_dict:
        bar_splice=('T' + bar_splice[1:])
        #Get the module_list qr from the bar code 
        module_qr=BAR_dict[str(bar_splice)]
        #print("feeding_qr:", module_qr)
        server(module_qr)
        wire_name="G"+bar_code[4:]
        if mode=="production":
            start_page(wire_name)
        else: 
            start_page(wire_name,"feeding")
            #print(f"please place the wire {wire_name} in their specified turn on Position.")
    else:
        show_error_message(f"the scanned bar_code splice: {bar_code[3:]} does not exist in the structure")
        if mode== "production":
            start_page()
        else:
            start_page("","feeding")

def delete_entry_field(entry):
    entry.delete(0, tk.END)
    entry.after(700, delete_entry_field, entry)  # Schedule the function to run again after 2 seconds

####################################### return to First Page #######################################
def reset(mode):
    clear_window()
    
    #control_combo_end(end_relay)
    start_page("", mode)

def login(password, box):
    #print(password)
    if password.get()=="llgsPi7":
        clear_window()
        #control_combo_end(end_relay)
        start_page(wire_name="", mode="feeding")
        
    else:
        messagebox.showerror("Error", "Wrong Password")
        box.delete(0, tk.END)

def feeding():
    # Then some time later, to remove just the 'my_button_callback':
    clear_window()
    password = StringVar()
    window_header( "Password Verification")
    
    label_function("Enter Your password:", 0.5, 0.3,window, "white", size=24)
    box = Entry(window, width=100, font=("Arial", 12),textvariable=password,  background="#D5D5D5",justify="center",show="*")
    box.place(relx=0.5, rely=0.35, anchor="center")
    box.focus_force()
    box.bind('<Return>', lambda event: login(password,box))
    button_function(window, "exit", lambda : start_page(), 0.6, 0.5, gray_color)
    button_function(window, "Login", lambda : login(password,box ), 0.4, 0.5, green_color)

def test():
    UNIQUE_WIRES, QR_dict, BAR_dict=read_txt_file()
    test_splice="N02G2Dtest"
    
    #get the splice name from the bar code --> example:  N02G2D215 --> G2D215 delete the first 3 characters
    bar_splice= test_splice[3:]
    
    #Get the module_list qr from the bar code 
    module_qr=BAR_dict[str(bar_splice)]
    
    server(module_qr,"test")

def read_txt_again_data():
    #read txt file
    UNIQUE_WIRES, QR_dict, BAR_dict=read_txt_file()
    return UNIQUE_WIRES, QR_dict, BAR_dict

def handle_read_txt_click():
    # Call the function and assign its return values to variables
    global UNIQUE_WIRES, QR_dict, BAR_dict
    UNIQUE_WIRES, QR_dict, BAR_dict = read_txt_again_data()
    messagebox.showinfo("Data Update", "the txt file storing data was read and data is now updtaed.")

def start_page(wire_name="", mode="production", UNIQUE_WIRES="", QR_dict="", BAR_dict=""):
    global production_database
    global counter 
    counter=0
    # define a StringVar to store the text from the entry box
    global qr_var
    qr_var = StringVar()
    
    clear_window()
    production_database=ProductionDatabase()
    #reset the combo and counter
    #control_combo_end(end_relay)
    # create the first window
    window_header( "Qr Scan")
    
    # Add text above the entry box
    label_function("Scan the Bar code", 0.5, 0.3,window, "white", size=22)
    # entry box for QR code input
    entry_box=entry_function(qr_var, 0.5, 0.35)
    entry_box.focus_force()  # Set focus to the entry box
    
    if mode=="production":
        label_function("Production Mode", 0.5, 0.15,window, green_color, size=40)
        delete_entry_field(entry_box)
        entry_box.bind('<Return>', lambda event: start_processing(qr_var))  # Bind Enter key to start_processing function
        # button to start processing
        button_function(window, "TEST", lambda: test(), 0.6, 0.5, blue_color)
        # button to start processing
        button_function(window, "Feeding Mode", lambda : feeding(), 0.4, 0.5, yellow_color)
    else:
        label_function("Feeding Page", 0.5, 0.1,window, "yellow", size=40)
        entry_box.bind('<Return>', lambda event: start_processing(qr_var,"feeding"))  # Bind Enter key to start_processing function
        button_function(window, "Production Mode", lambda: start_page(), 0.2, 0.5, green_color)
        # button to start processing
        button_function(window, "TEST", lambda: test(), 0.4, 0.5, blue_color)
        #table button
        button_function(window,"Data", lambda: show_table_data(), 0.6, 0.5, yellow_color)
        #update the data manually after loading it throught the use of the configugration application
        button_function(window, "Read New Data", lambda : handle_read_txt_click(), 0.8, 0.5, green_color)
        # button to start processing
        button_function(window, "RESET", lambda : reset(mode), 0.9, 0.9, gray_color)
        # button to plot data
        button_function(window, "Plot data", lambda : plot(), 0.5, 0.6, green_color)
        
    # button to start processing
    #button_function(window, "START", lambda: start_processing(qr_var), 0.3, 0.5, green_color)
    
    if wire_name!="":
        label_function(f"Place the following wire in the specified position where the LED is turned on.", 0.5, 0.65, window, "white", 24)
        label_function(wire_name, 0.5, 0.7, window, gray_color, 28)
        
    #exit button to kill script execution
    #button_function(window,"EXIT", lambda: kill_script(), 0.7, 0.6)
    assign_qr(entry_box)

# Create the first window
window = Tk()

#responsive design for the interface
global screen_width, screen_height
screen_width=window.winfo_screenwidth()
screen_height=window.winfo_screenheight()
#print(screen_width, screen_height)
#read txt file
UNIQUE_WIRES, QR_dict, BAR_dict=read_txt_file()

# Set the window title
window.title("LLGS application")
window.bind('=', lambda event: kill_script())
start_page("", "production", UNIQUE_WIRES, QR_dict, BAR_dict )
window.mainloop()