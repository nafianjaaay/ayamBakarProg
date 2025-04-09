import pathlib
import pygubu
import time
import tkinter as tk
from tkinter import font
from PIL import Image, ImageTk
import os
from datetime import datetime
import threading
import RPi.GPIO as GPIO

PROJECT_PATH = pathlib.Path(__file__).parent
PROJECT_UI = PROJECT_PATH / "visualisasi_img.ui"

GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.OUT)

class SerialThread(threading.Thread):
    def __init__(self, app):
        super().__init__()
        self.app = app
    
    def run(self):
        while True:
            try:
                c = datetime.now()
                self.current_time = c.strftime('%H:%M:%S')
                #print(self.current_time)
                
                app.update_spc_timestamp(self.current_time)
            except:
                pass
                
    def entry_input(self, event=None):
        def submit(event=None):
            global entered_value
            entered_value = entry.get()
            app.value = int(entered_value)
            root.destroy()
        # Create the main window
        root = tk.Tk()
        root.title("Entry Example")
        
        # ~ root.geometry("300x150")

        # Create a label
        label = tk.Label(root, text="Enter something:", font=("Arial", 36))
        label.pack()

        # Create an entry widget with width 30 and adjusted font size
        entry = tk.Entry(root, width=30, font=("Arial", 48))
        entry.pack()
        entry.focus()  # Set focus to entry widget

        # Bind the Enter key to submit the entry
        entry.bind("<Return>", submit)
        entry.bind("<KP_Enter>", submit)

        # Create a submit button
        submit_button = tk.Button(root, text="Submit", command=submit)
        submit_button.pack()

        # Run the Tkinter event loop
        root.mainloop()
        
        # ~ print("You entered:", entered_value)

class App:

    def __init__(self, master=None):
        #jumlah item per jam
        self.value = 1706
        #jumlah item per shift
        self.shift1 = 13650
        self.shift2 = 12450
        self.shift3 = 12150
        
        #declare, jangan diubah!
        self.input1_value = 0
        self.input2_value = 0
        self.input3_value = 0
        self.increment_value = 0
        self.result = 0
        self.time_value = 0
        self.sum_value = 0
        self.display_value = 0
        self.hour_target = 0
        
        self.plus1 = 0
        self.plus2 = 0
        self.plus3 = 0
        self.plus4 = 0
        self.plus5 = 0
        self.plus6 = 0
        self.plus7 = 0
        self.plus8 = 0
        self.total = 0
        
        self.onoff = "Off"

        self.builder = builder = pygubu.Builder()
        builder.add_resource_path(PROJECT_PATH)
        builder.add_from_file(PROJECT_UI)
        self.mainwindow = builder.get_object("toplevel1", master)
        self.mainwindow.attributes("-fullscreen", True)
        builder.connect_callbacks(self)
        # ~ self.mainwindow.bind('<KP_Enter>', self.update_spc_status)
        # ~ self.mainwindow.bind('<Return>', self.update_spc_status)
        self.status_canvas = tk.Canvas(self.mainwindow, width=100, height=100, highlightthickness=0, bg="#051401")
        self.status_canvas.place(x=25, y=20)
        self.status_circle = self.status_canvas.create_oval(0, 0, 80, 80, fill="chartreuse")
        self.status_is_red = False  # Default warna: hijau
        self.status_canvas2 = tk.Canvas(self.mainwindow, width=100, height=100, highlightthickness=0, bg="#051401")
        self.status_canvas2.place(x=25, y=120)
        self.status_circle2 = self.status_canvas2.create_oval(0, 0, 80, 80, fill="chartreuse")
        self.status2_is_red = False  # Default warna hijau
        self.mainwindow.bind('<KP_4>', self.one)
        self.mainwindow.bind('<KP_2>', self.ten)
        self.mainwindow.bind('<KP_6>', self.fifty)
        self.mainwindow.bind('<KP_Subtract>', self.minhundred)
        self.mainwindow.bind('<KP_Enter>', self.hundred)
        self.mainwindow.bind('<KP_9>', self.toggle_grok_image)
        self.mainwindow.bind('<KP_7>', self.toggle_grok2_image)
        self.mainwindow.bind('<KP_5>', self.toggle_status_color)
        self.mainwindow.bind('<KP_0>', self.toggle_status_color2)

    
        self.input1_var = self.builder.get_object("label2")
        self.input2_var = self.builder.get_object("label4")
        self.input3_var = self.builder.get_object("label6")
        
        self.count1_var = self.builder.get_object("label19")
        self.count2_var = self.builder.get_object("label20")
        self.count3_var = self.builder.get_object("label21")
        self.count4_var = self.builder.get_object("label22")
        self.count5_var = self.builder.get_object("label23")
        self.count6_var = self.builder.get_object("label24")
        self.count7_var = self.builder.get_object("label25")
        self.count8_var = self.builder.get_object("label26")
        
        self.serial_thread = None
        self.grok_image_visible = False  # Status toggle
        self.grok_label = None           # Tempat label gambarnya
        
        self.main_assy_label = tk.Label(
            self.mainwindow,
            text="MAIN ASSY",
            font=("Helvetica", 24, "bold"),
            bg="#051401", 
            fg="white"    
        )
        self.main_assy_label.place(relx=0.0, rely=0.0, x=120, y=45, anchor='nw')
        
        self.sub_assy_label = tk.Label(
            self.mainwindow,
            text="SUB ASSY",
            font=("Helvetica", 24, "bold"),
            bg="#051401", 
            fg="white"    
        )
        self.sub_assy_label.place(relx=0.0, rely=0.0, x=120, y=145, anchor='nw')  
        # sub


        # Load image
        image_path = "/home/pi/Desktop/visualisasi_g2r/grok.png"
        self.grok_img = Image.open(image_path)
        self.grok_img = self.grok_img.resize((726, 483), Image.ANTIALIAS)
        self.grok_photo = ImageTk.PhotoImage(self.grok_img)
        self.start_serial_thread()
        self.clock_label = tk.Label(self.mainwindow, font=("Roboto", 30), fg="yellow", bg="#051401")
        self.clock_label.place(x=15, rely=0.99, anchor='sw')
        self.update_clock()

        
    def run(self):
        self.mainwindow.mainloop()

    def start_serial_thread(self):
        if not self.serial_thread or not self.serial_thread.is_alive():
            self.serial_thread = SerialThread(self)
            self.serial_thread.start()
        else:
            print("Serial thread is already running.")
    
    # ~ def update_spc_status(self, status):    
        # ~ self.input2_value += self.increment_value
        # ~ self.input1_var.config(text=str(self.input1_value))
        # ~ self.input2_var.config(text=str(self.input2_value))
    
        # ~ self.display_value += self.increment_value
    
        # ~ if self.hour_target > self.input2_value:
            # ~ self.input2_var.config(bg="#ff4500")
        # ~ elif self.hour_target <= self.input2_value:
            # ~ self.input2_var.config(bg="green")
            
    
            
    def one(self, status):
        self.increment_value = 1
        self.input2_value += self.increment_value
        self.input1_var.config(text=str(self.input1_value))
        self.input2_var.config(text=str(self.input2_value))
    
        self.display_value += self.increment_value
    
        # ~ if self.hour_target > self.input2_value:
            # ~ self.input2_var.config(bg="#ff4500")
        if self.hour_target <= self.input2_value:
            self.input2_var.config(bg="#4169e1")
        # ~ print(self.value)
        
    def ten(self, status):
        self.increment_value = 10
        self.input2_value += self.increment_value
        self.input1_var.config(text=str(self.input1_value))
        self.input2_var.config(text=str(self.input2_value))
    
        self.display_value += self.increment_value
    
        # ~ if self.hour_target > self.input2_value:
            # ~ self.input2_var.config(bg="#ff4500")
        if self.hour_target <= self.input2_value:
            self.input2_var.config(bg="#4169e1")

    def fifty(self, status):
        self.increment_value = 50
        self.input2_value += self.increment_value
        self.input1_var.config(text=str(self.input1_value))
        self.input2_var.config(text=str(self.input2_value))
    
        self.display_value += self.increment_value
    
        # ~ if self.hour_target > self.input2_value:
            # ~ self.input2_var.config(bg="#ff4500")
        if self.hour_target <= self.input2_value:
            self.input2_var.config(bg="#4169e1")
            
    def minhundred(self, status):
        self.increment_value = -100
        self.input2_value += self.increment_value
        self.input1_var.config(text=str(self.input1_value))
        self.input2_var.config(text=str(self.input2_value))
    
        self.display_value += self.increment_value
    
        if self.hour_target > self.input2_value:
            self.input2_var.config(bg="#ff4500")
        if self.hour_target <= self.input2_value:
            self.input2_var.config(bg="#4169e1")
        
    def hundred(self, status):
        self.increment_value = 100
        self.input2_value += self.increment_value
        self.input1_var.config(text=str(self.input1_value))
        self.input2_var.config(text=str(self.input2_value))
    
        self.display_value += self.increment_value
    
        # ~ if self.hour_target > self.input2_value:
            # ~ self.input2_var.config(bg="#ff4500")
        if self.hour_target <= self.input2_value:
            self.input2_var.config(bg="#4169e1")
        
        GPIO.output(22, 0)
        time.sleep(0.015)
        GPIO.output(22, 1)
        
    def update_clock(self):
        now = datetime.now().strftime('%H:%M:%S')
        self.clock_label.config(text=now)
        self.mainwindow.after(1000, self.update_clock)
        
    def toggle_status_color(self, event=None):
        if self.status_is_red:
            self.status_canvas.itemconfig(self.status_circle, fill="chartreuse")
        else:
            self.status_canvas.itemconfig(self.status_circle, fill="orange red")
        self.status_is_red = not self.status_is_red
        
    def toggle_status_color2(self, event=None):
        if self.status2_is_red:
            self.status_canvas2.itemconfig(self.status_circle2, fill="chartreuse")
        else:
            self.status_canvas2.itemconfig(self.status_circle2, fill="orange red")
        self.status2_is_red = not self.status2_is_red
        
    def toggle_grok_image(self, event=None):
        if not hasattr(self, 'grok_visible'):
            self.grok_visible = False

        self.grok_visible = not self.grok_visible

        if self.grok_visible:
            self.grok_img = Image.open("/home/pi/Desktop/visualisasi_g2r/grok.png")
            self.grok_img = self.grok_img.resize((721, 481), Image.ANTIALIAS)
            self.grok_photo = ImageTk.PhotoImage(self.grok_img)

            self.grok_label = tk.Label(self.mainwindow, image=self.grok_photo, bg="yellow")
            self.grok_label.place(relx=0, rely=0.5, anchor="center")

            self.grok_blinking = True
            self.blink_grok()
        else:
            self.grok_blinking = False
            self.grok_label.destroy()

    def blink_grok(self):
        if not self.grok_blinking:
            return

        if self.grok_label.winfo_viewable():
            self.grok_label.place_forget()
        else:
            self.grok_label.place(relx=0.5, rely=0.5, anchor="center")

        self.mainwindow.after(1250, self.blink_grok)
        
    def toggle_grok2_image(self, event=None):
        if not hasattr(self, 'grok2_visible'):
            self.grok2_visible = False

        self.grok2_visible = not self.grok2_visible

        if self.grok2_visible:
            self.grok2_img = Image.open("/home/pi/Desktop/visualisasi_g2r/grok2.png")
            self.grok2_img = self.grok2_img.resize((721, 481), Image.ANTIALIAS)
            self.grok2_photo = ImageTk.PhotoImage(self.grok2_img)

            self.grok2_label = tk.Label(self.mainwindow, image=self.grok2_photo, bg="yellow")
            self.grok2_label.place(relx=0.5, rely=0.5, anchor="center")

            self.grok2_blinking = True
            self.blink_grok2()
        else:
            self.grok2_blinking = False
            self.grok2_label.destroy()

    def blink_grok2(self):
        if not self.grok2_blinking:
            return

        if self.grok2_label.winfo_viewable():
            self.grok2_label.place_forget()
        else:
            self.grok2_label.place(relx=0.5, rely=0.5, anchor="center")

        self.mainwindow.after(1250, self.blink_grok2)
            
    def update_spc_timestamp(self, timestamp):
        self.time_value = timestamp
        try:
            #shift 1
            if timestamp == "07:55:00":
                #total item shift 1
                self.hour_target = self.value * 2
                self.input1_value = self.hour_target
                #self.input1_value = self.shift1
                #self.input2_value = 0
                #self.display_value = 0
                self.input3_value = self.input2_value - self.input1_value
                self.input1_var.config(text=str(self.input1_value))
                #self.input2_var.config(text=str(self.input2_value))
                #self.input3_var.config(text=str(self.input3_value))
                self.sum_value = self.value
                self.result = self.display_value - self.value
                print(self.sum_value)
                print(self.display_value)
                print(self.result)
                self.count1_var.config(text=str(self.result))
                #self.input2_var.config(text=str(self.input2_value))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count1_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count1_var.config(bg="green")
                    
                #self.hour_target = self.value * 2
                
                self.plus1 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                
                
                time.sleep(1)
                self.display_value = 0
                    
            elif timestamp == "08:55:00":
                self.hour_target = self.value * 3
                self.input1_value = self.hour_target
                #self.input1_value = self.shift1
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 2
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count2_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count2_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count2_var.config(bg="green")
                    
                #self.hour_target = self.value * 3
                
                self.plus2 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                
                time.sleep(1)
                self.display_value = 0
                    
            elif timestamp == "09:55:00":
                self.hour_target = self.value * 4
                self.input1_value = self.hour_target
                #self.input1_value = self.shift1
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 3
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count3_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count3_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count3_var.config(bg="green")
                    
                #self.hour_target = self.value * 4
                
                self.plus3 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
            
            elif timestamp == "10:55:00":
                self.hour_target = self.value * 5
                self.input1_value = self.hour_target
                #self.input1_value = self.shift1
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 4
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count4_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count4_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count4_var.config(bg="green")
                    
                #self.hour_target = self.value * 5
                
                self.plus4 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                    
            elif timestamp == "11:55:00":
                self.hour_target = self.value * 6
                self.input1_value = self.hour_target
                #self.input1_value = self.shift1
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 5
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count5_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count5_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count5_var.config(bg="green")
                    
                #self.hour_target = self.value * 6
                
                self.plus5 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                    
            elif timestamp == "13:40:00":
                self.hour_target = self.value * 7
                self.input1_value = self.hour_target
                #self.input1_value = self.shift1
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 6
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count6_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count6_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count6_var.config(bg="green")
                    
                #self.hour_target = self.value * 7
                
                self.plus6 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                    
            elif timestamp == "14:40:00":
                self.hour_target = self.value * 8
                self.input1_value = self.hour_target
                #self.input1_value = self.shift1
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 7
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count7_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count7_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count7_var.config(bg="green")
                    
                #self.hour_target = self.value * 8
                
                self.plus7 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                time.sleep(1)
                self.display_value = 0
                    
            elif timestamp == "15:40:00":
                #self.input1_value = self.sum_value
                self.sum_value = self.value * 8
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count8_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                #elif self.sum_value > self.input2_value:
                #   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count8_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count8_var.config(bg="green")
                    
                self.plus8 = self.result
                # ~ self.total = self.input2_value - self.sum_value
                # ~ self.input3_var.config(text=str(0))
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                #total item shift 2
                self.hour_target = self.value
                self.input1_value = self.hour_target
                #self.input1_value = self.shift2
                self.input2_value = 0
                self.display_value = 0
                self.input3_value = self.input2_value - self.input1_value
                self.input1_var.config(text=str(self.input1_value))
                self.input2_var.config(text=str(self.input2_value))
                # ~ self.input3_var.config(text=str(self.input3_value))
                self.input3_var.config(text=str(0))
                self.display_value = 0
                
                # ~ self.hour_target = self.value
                
            #shift 2
            if timestamp == "15:55:00":
                #self.input1_value = self.shift2
                self.hour_target = self.value
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.count1_var.config(text=str(""), bg="#166fc0")
                self.count2_var.config(text=str(""), bg="#166fc0")
                self.count3_var.config(text=str(""), bg="#166fc0")
                self.count4_var.config(text=str(""), bg="#166fc0")
                self.count5_var.config(text=str(""), bg="#166fc0")
                self.count6_var.config(text=str(""), bg="#166fc0")
                self.count7_var.config(text=str(""), bg="#166fc0")
                self.count8_var.config(text=str(""), bg="#166fc0")
                self.plus1 = 0
                self.plus2 = 0
                self.plus3 = 0
                self.plus4 = 0
                self.plus5 = 0
                self.plus6 = 0
                self.plus7 = 0
                self.plus8 = 0
            if timestamp == "16:40:00":
                self.hour_target = self.value * 2
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value
                self.result = self.display_value - self.value
                print(self.sum_value)
                print(self.display_value)
                print(self.result)
                self.count1_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count1_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count1_var.config(bg="green")
                    
                self.hour_target = self.value * 2
                
                self.plus1 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                
                time.sleep(1)
                self.display_value = 0
                
            elif timestamp == "17:40:00":
                self.hour_target = self.value * 3
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 2
                self.result = self.display_value - self.value
                print(self.sum_value)
                print(self.display_value)
                print(self.result)
                self.count2_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count2_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count2_var.config(bg="green")
                    
                self.hour_target = self.value * 3
                
                self.plus2 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                
                time.sleep(1)
                self.display_value = 0
            
            elif timestamp == "19:20:00":
                self.hour_target = self.value * 4
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 3
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count3_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count3_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count3_var.config(bg="green")
                    
                self.hour_target = self.value * 4
                
                self.plus3 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
            
            elif timestamp == "20:20:00":
                self.hour_target = self.value * 5
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 4
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count4_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count4_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count4_var.config(bg="green")
                    
                self.hour_target = self.value * 5
                
                self.plus4 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                
            elif timestamp == "21:20:00":
                self.hour_target = self.value * 6
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 5
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count5_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count5_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count5_var.config(bg="green")
                    
                self.hour_target = self.value * 6
                
                self.plus5 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                
            elif timestamp == "22:20:00":
                self.hour_target = self.value * 7
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 6
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count6_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count6_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count6_var.config(bg="green")
                    
                self.hour_target = self.value * 7
                
                self.plus6 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                
            elif timestamp == "23:20:00":
                self.sum_value = self.value * 7
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count7_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                # ~ elif self.sum_value > self.input2_value:
                   # ~ self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count7_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count7_var.config(bg="green")
                    
                self.plus7 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                #Total item Shift 3
                self.hour_target = self.value
                self.input1_value = self.hour_target
                self.input2_value = 0
                self.display_value = 0
                self.input3_value = self.input2_value - self.input1_value
                self.input1_var.config(text=str(self.input1_value))
                self.input2_var.config(text=str(self.input2_value))
                # ~ self.input3_var.config(text=str(self.input3_value))
                self.input3_var.config(text=str(0))
                self.display_value = 0
                
                self.hour_target = self.value
                
            #shift 3    
            if timestamp == "23:35:00":
                self.hour_target = self.value
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.count1_var.config(text=str(""), bg="#166fc0")
                self.count2_var.config(text=str(""), bg="#166fc0")
                self.count3_var.config(text=str(""), bg="#166fc0")
                self.count4_var.config(text=str(""), bg="#166fc0")
                self.count5_var.config(text=str(""), bg="#166fc0")
                self.count6_var.config(text=str(""), bg="#166fc0")
                self.count7_var.config(text=str(""), bg="#166fc0")
                self.count8_var.config(text=str(""), bg="#166fc0")
                self.plus1 = 0
                self.plus2 = 0
                self.plus3 = 0
                self.plus4 = 0
                self.plus5 = 0
                self.plus6 = 0
                self.plus7 = 0
                self.plus8 = 0
            if timestamp == "00:20:00":
                self.hour_target = self.value * 2
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count1_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count1_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count1_var.config(bg="green")
                    
                self.hour_target = self.value * 2
                
                self.plus1 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                
            elif timestamp == "01:20:00":
                self.hour_target = self.value * 3
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 2
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count2_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count2_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count2_var.config(bg="green")
                    
                self.hour_target = self.value * 3
                
                self.plus2 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                
            elif timestamp == "02:20:00":
                self.hour_target = self.value * 4
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 3
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count3_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count3_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count3_var.config(bg="green")
                    
                self.hour_target = self.value * 4
                
                self.plus3 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                
            elif timestamp == "03:50:00":
                self.hour_target = self.value * 5
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 4
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count4_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count4_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count4_var.config(bg="green")
                    
                self.hour_target = self.value * 5
                
                self.plus4 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                
            elif timestamp == "04:50:00":
                self.hour_target = self.value * 6
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 5
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count5_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count5_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count5_var.config(bg="green")
                    
                self.hour_target = self.value * 6
                
                self.plus5 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                
            elif timestamp == "06:05:00":
                self.hour_target = self.value * 7
                self.input1_value = self.hour_target
                self.input1_var.config(text=str(self.input1_value))
                self.sum_value = self.value * 6
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count6_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                elif self.sum_value > self.input2_value:
                   self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count6_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count6_var.config(bg="green")
                    
                self.hour_target = self.value * 7
                
                self.plus6 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                self.display_value = 0
                
            elif timestamp == "06:55:00":
                self.sum_value = self.value * 7
                self.result = self.display_value - self.value
                print(self.sum_value)
                self.count7_var.config(text=str(self.result))
                # ~ if self.input2_value < self.sum_value:
                    # ~ self.input2_var.config(bg="#ff4500")
                # ~ elif self.input2_value >= self.sum_value:
                    # ~ self.input2_var.config(bg="green")
                if self.sum_value <= self.input2_value:
                   self.input2_var.config(bg="green")
                # ~ elif self.sum_value > self.input2_value:
                   # ~ self.input2_var.config(bg="#ff4500")
                   
                if(self.result < 0):
                    self.count7_var.config(bg="#ff4500")
                elif(self.result >= 0):
                    self.count7_var.config(bg="green")
                    
                self.plus7 = self.result
                self.total = self.input2_value - self.sum_value
                self.input3_var.config(text=str(self.total))
                    
                time.sleep(1)
                #total item shift 1
                self.hour_target = self.value
                self.input1_value = self.hour_target
                self.input2_value = 0
                self.display_value = 0
                self.input3_value = self.input2_value - self.input1_value
                self.input1_var.config(text=str(self.input1_value))
                self.input2_var.config(text=str(self.input2_value))
                # ~ self.input3_var.config(text=str(self.input3_value))
                self.input3_var.config(text=str(0))
                self.display_value = 0
                
                self.hour_target = self.value
            
            elif timestamp == "07:10:00":
                self.count1_var.config(text=str(""), bg="#166fc0")
                self.count2_var.config(text=str(""), bg="#166fc0")
                self.count3_var.config(text=str(""), bg="#166fc0")
                self.count4_var.config(text=str(""), bg="#166fc0")
                self.count5_var.config(text=str(""), bg="#166fc0")
                self.count6_var.config(text=str(""), bg="#166fc0")
                self.count7_var.config(text=str(""), bg="#166fc0")
                self.count8_var.config(text=str(""), bg="#166fc0")
                self.plus1 = 0
                self.plus2 = 0
                self.plus3 = 0
                self.plus4 = 0
                self.plus5 = 0
                self.plus6 = 0
                self.plus7 = 0
                self.plus8 = 0
            
            # ~ print(self.hour_target)
        except:
            pass
    
if __name__ == '__main__':
    app = App()
    app.run()
