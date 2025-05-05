import paho.mqtt.client as mqtt
import customtkinter as ctk

def reset_dashboard():
    # Function to reset all counters and labels
    global total_labels, list_labels, total_frames, title_frames, list_frames, counters
    
    # Reset counters and labels
    total_labels = {}
    list_labels = {}
    total_frames = {}
    title_frames = {}
    list_frames = {}
    counters = {}

    # Reinitialize the dashboard
    dashboard_frame()
    
def label_function(name, relx, rely, root, size=24, bgcolor="transparent", color="black"):
# excel path label
    scan_text = ctk.CTkLabel(root, text=name, font=("Helvetica", size,'bold'), fg_color=bgcolor, padx=0, corner_radius=0, text_color=color)
    scan_text.place(relx=relx, rely=rely, anchor="center")
    return scan_text

def handle_mqtt_message(message, frame_name, total_label, list_label,title_frames, total_frames, list_frames):
    received_message = str(message.payload.decode("utf-8"))
    print("Received message for frame", frame_name, ":", received_message)

    # Split the received message into hostname and reference name
    hostname, reference_name = received_message.split("@")
    print("reference_name is ",reference_name)
    
    if reference_name!= "end" :
        print("not end")
        title_frames.configure(fg_color="green")
        list_frames.configure(fg="green")
        # Initialize counters if not already initialized
        if 'counters' not in handle_mqtt_message.__dict__:
            handle_mqtt_message.counters = {}

        # Initialize counters for the frame and reference names if not already initialized
        if frame_name not in handle_mqtt_message.counters:
            handle_mqtt_message.counters[frame_name] = {}
            handle_mqtt_message.counters[frame_name]["total"] = 0

        if reference_name not in handle_mqtt_message.counters[frame_name]:
            handle_mqtt_message.counters[frame_name][reference_name] = 1
        else:
            handle_mqtt_message.counters[frame_name][reference_name] += 1

        # Update total label with the counter value for the frame
        handle_mqtt_message.counters[frame_name]["total"] += 1
        total_label.configure(text=str(handle_mqtt_message.counters[frame_name]["total"]))

        # Update the list label
        list_content = ""
        for ref_name, counter in handle_mqtt_message.counters[frame_name].items():
            if ref_name == "total":
                continue
            list_content += f"{ref_name} {counter}\n"

        list_label.configure(text=list_content)
    elif reference_name=="end":
        print("end")
        title_frames.configure(fg="white")
        list_frames.configure(fg="white") 
          
def dashboard_frame():
    root.bind("<Key>", lambda event: root.after(1000, reset_dashboard))  # 24 hours in milliseconds
    
    # parent frame
    frame = ctk.CTkFrame(master=root, border_width=3, fg_color="black") 
    frame.pack(pady=0, padx=0, fill='both', expand=True) 
    
    # dimensions of sub frames    
    frame_width = frame.winfo_screenwidth() 
    frame_height = frame.winfo_screenheight()
    print(frame_width, frame_height)
    
    sub_frame_width = frame_width / 3 
    sub_frame_height = frame_height / 2
    sub_sub_frame_height = sub_frame_height / 8
    
    # Define frame names and labels
    frame_data = [
        ("DESKTOP-L36SUP5", "N02"),
        ("LLGS002", "N01"),
        ("LLGS003", "L01"),
        ("LLGS004", "L02"),
        ("LLGS005", "U01"),
        ("LLGS006", "U02")
    ]
    
    # Create frames dynamically
    total_labels = {}
    list_labels = {}
    total_frames = {}
    title_frames={}
    list_frames={}
    for i, (frame_name, label_name) in enumerate(frame_data):
        # Calculate row and column for grid
        row = i // 3
        column = i % 3
        
        # Create frame
        frame_instance = ctk.CTkFrame(master=frame, border_width=2, border_color="black", width=sub_frame_width, height=sub_frame_height)
        frame_instance.grid(row=row, column=column)
        
        # Create title
        title_frames[frame_name] = ctk.CTkFrame(master=frame_instance, width=sub_frame_width, height=sub_sub_frame_height, fg_color="white")
        title_frames[frame_name].grid(row=0, column=0, padx=2, pady=2)
        label_function(label_name, 0.5, 0.5, title_frames[frame_name], 40, "white", "black")
        
        # Create total label
        total_frames[frame_name] = ctk.CTkFrame(master=frame_instance, width=sub_frame_width, height=sub_sub_frame_height*2, fg_color="black")
        total_frames[frame_name].grid(row=1, column=0, padx=2)
        total_labels[frame_name] = label_function("0 Collected", 0.5, 0.5, total_frames[frame_name], 40, "black", "white")
        
        # Create list label
        list_frames[frame_name] = ctk.CTkFrame(master=frame_instance, width=sub_frame_width, height=sub_sub_frame_height*5, fg_color="white")
        list_frames[frame_name].grid(row=2, column=0, padx=2, pady=2)
        list_labels[frame_name] = label_function("list", 0.5, 0.5, list_frames[frame_name], 24, "white", "black")
    
    # MQTT broker address and port
    broker_address = "localhost"  # Assuming MQTT broker is running locally
    port = 1883  # Default MQTT port

    # Connect to the MQTT broker
    client = mqtt.Client()
    client.connect(broker_address, port)

    # Subscribe to the single MQTT topic
    client.subscribe("LLGS")

    # Define callback function for MQTT messages
    
    def on_message(client, userdata, message):
        print(message)
        msg= str(message.payload.decode("utf-8")).split("@")
        if msg=="DESKTOP-L36SUP5":
            handle_mqtt_message(message, "DESKTOP-L36SUP5", total_labels["DESKTOP-L36SUP5"], list_labels["DESKTOP-L36SUP5"], title_frames["DESKTOP-L36SUP5"], total_frames["DESKTOP-L36SUP5"],list_frames["DESKTOP-L36SUP5"])
        elif msg=="LLGS002":
            handle_mqtt_message(message, "LLGS002", total_labels["LLGS002"], list_labels["LLGS002"],title_frames["LLGS002"], total_frames["LLGS002"], list_frames["LLGS002"])
        elif msg=="LLGS003":
            handle_mqtt_message(message, "LLGS003", total_labels["LLGS003"], list_labels["LLGS003"],title_frames["LLGS003"], total_frames["LLGS003"], list_frames["LLGS003"])
        elif msg=="LLGS004":
            handle_mqtt_message(message, "LLGS004", total_labels["LLGS004"], list_labels["LLGS004"],title_frames["LLGS004"], total_frames["LLGS004"], list_frames["LLGS004"])
        elif msg=="LLGS005":
            handle_mqtt_message(message, "LLGS005", total_labels["LLGS005"], list_labels["LLGS005"],title_frames["LLGS005"], total_frames["LLGS005"], list_frames["LLGS005"])
    # Set callback function for MQTT message reception
    client.on_message = on_message

    # Start the MQTT loop
    client.loop_start()

# Create the main tk instance
root = ctk.CTk()
ctk.set_appearance_mode("light")
root.attributes('-fullscreen', True)
# Maximize the window
root.after(0, lambda: root.state("zoomed")) #this line is responsible for making the display full screen, if commented you only get a quarter if the screen shown
# Set the window title
root.title("Create Configuration File")

root.bind("=",lambda event: root.destroy())
#root.wm_iconbitmap("images/Lear_L_Logo-removebg-preview-removebg-preview.ico")
#call the first page window function
dashboard_frame()
# Run the Tkinter event loop
root.mainloop() 