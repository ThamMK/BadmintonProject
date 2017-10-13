# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 01:13:21 2017

@author: Shiangyoung
"""

import sys

if sys.version_info.major == 2:
    from Tkinter import *
    import  tkFileDialog as filedialog
    import Tkinter as tk     # python 2
    import tkFont as tkfont
    import tkMessageBox as messagebox # python 2
else:
    from tkinter import *
    from tkinter import filedialog,messagebox,Canvas
    import tkinter as tk                # python 3
    from tkinter import font  as tkfont # python 3
    
import ttk
import os
import cv2
import sys
from multiprocessing import Process
import subprocess,psutil
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import neural_network as nn

def global_paths():
    
    global VIDEO_FILE_PATH
    global FIRST_ACCESS_START
    
    VIDEO_FILE_PATH = None
    FIRST_ACCESS_START = True
    

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.body_font = tkfont.Font(family='Helvetica', size=10)
        
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, PageThree):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        
    def close_all_window(self):
        app.destroy()
        app.quit()
        sys.exit()


class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="This is the start page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Go to Page One",
                            command=lambda: controller.show_frame("PageOne"))
        button2 = tk.Button(self, text="Go to Page Two",
                            command=lambda: controller.show_frame("PageTwo"))
        button3 = tk.Button(self, text="Go to Page Three",
                            command=lambda: controller.show_frame("PageThree"))
        button1.pack()
        button2.pack()
        button3.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        instruction = Label(self,text="Please select a file:")
        instruction.grid(row=0,column=0,padx=(10,0),pady=(10,0),sticky=W)
        instruction.config(font=controller.body_font) 
        
        self.fileE = Entry(self,width=50,bg="white")
        self.fileE.config(state='disabled',font=controller.body_font)
        self.fileE.grid(row=1,column=0,padx=(10,3),pady=(5,5),columnspan=3)
        
        fileB = Button(self,text="Browse...",command=self.browse_file,height = 1,width=10)
        fileB.grid(row=1,column=4,padx=(4,10))
        
        self.nextB = Button(self,text="Next",width=10,command=self.check_file_valid)
        self.nextB.config(state='disabled')
        self.nextB.grid(row=2,column=2,sticky=E,pady=(20,5),padx=(0,5))
        
        cancelB = Button(self,text="Quit",width=10,command=self.controller.close_all_window)
        cancelB.grid(row=2,column=4,sticky=W,pady=(20,5),padx=(4,10))
        
    def browse_file(self):
        fname = filedialog.askopenfilename()
        
        if not(type(fname) == tuple or fname == ""):
            self.fileE.config(state='normal')
            self.nextB.config(state='normal')         
            self.fileE.delete('0',END)
            self.fileE.insert('0',fname)
        else:
            self.fileE.delete('0',END)
            self.fileE.insert('0',"")
            self.fileE.config(state='disabled')
            self.nextB.config(state='disabled')         
        
        print(fname)
        
        global VIDEO_FILE_PATH
        VIDEO_FILE_PATH = fname
        
    def check_file_valid(self):
        global VIDEO_FILE_PATH
        global FIRST_ACCESS_START        
        
        VIDEO_FILE_PATH = self.fileE.get()
        basename = os.path.basename(VIDEO_FILE_PATH)
        basename = os.path.splitext(basename)[0]
        if(os.path.exists(VIDEO_FILE_PATH)):
            self.controller.show_frame("PageTwo")
        else:
            messagebox.showerror("File is not exist","The file (" + basename  + ") is not found. Please choose a file that is valid.")

class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        instruction = Label(self,text="Press start to progress the file",anchor="w")
        instruction.pack(fill="both",pady = (10,5),padx = (10,0))
        instruction.config(font=controller.body_font)        
        
        # Progress Bar        
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.progress = ttk.Progressbar(self, style="green.Horizontal.TProgressbar", orient="horizontal", length=500, mode="determinate")
        self.progress.pack(fill="both", padx = (10,10))
        
        center = Frame(self)
        
        self.progressLabel = Label(self,text="0%")
        self.progressLabel.pack(in_ = center,padx = (10,0),side=LEFT)    
        self.progressLabel.config(font=controller.body_font)
        
        self.buttonStart = Button(self,text="Start",width=8,command=self.start)
        self.buttonStart.pack(in_ = center, padx=(0,10),side=RIGHT)
        
        center.pack(fill=BOTH,pady=(10,0))
        
        horizontal_line = ttk.Separator(self,orient=HORIZONTAL)
        horizontal_line.pack(pady = (15,5),padx = (10,10),fill=BOTH)
        
        bottom = Frame(self)
        
        buttonQuit= Button(self,text="Quit",width=8,command=self.close_current_window)
        buttonQuit.pack(in_=bottom,side=RIGHT,padx = (0,10))
        
        self.buttonNext= Button(self,text="Next",width=8,command=lambda: controller.show_frame("PageThree"))
        self.buttonNext.pack(in_=bottom,side=RIGHT,padx = (0,10))
        self.buttonNext.config(state='disabled')
        
        self.buttonBack= Button(self,text="Back",width=8,command=lambda: controller.show_frame("PageOne"))
        self.buttonBack.pack(in_=bottom,side=RIGHT,padx = (0,10))
        
        bottom.pack(fill=BOTH,pady=(10,10))
        
        # Variables to update the progress bar
        self.val = 0
        self.maxval = 1
        self.progress["maximum"] = 1
        
    def testing(self):
        print("hihi")

    def updating(self, val):
        self.val = val
        self.progress["value"] = self.val
        current_progress = '{:.2f}'.format(self.val*100)
        self.progressLabel.config(text=current_progress+"%")
        
        #should change to available for next button once it is finish
        if self.val == self.maxval:
            self.buttonNext.config(state='normal')
            self.buttonBack.config(state='normal')
            self.buttonStart.config(state='disabled')
    
    def calculate_files(self):
        
        direct =  os.getcwd() + "/output"
        list = os.listdir(direct) # dir is your directory path
        number_files = len(list)
        return number_files

    def check_file(self,i=0):
        self.updating(i/ float(self.length))
        if(i/float(self.length) < 1.0):
            self.after(100, self.check_file, self.calculate_files())
            
    def functionA(self):
        self.after(1, self.check_file)
        
    def functionB(self):
        
        #os.system(cmd)
        subprocess.Popen(self.cmd, stdout=subprocess.PIPE,shell=True, preexec_fn=os.setsid) 
        
    def start(self):
        
        global VIDEO_FILE_PATH
        global FIRST_ACCESS_START
        
        self.cmd = "./build/examples/openpose/openpose.bin --video " + VIDEO_FILE_PATH +" --no_display --write_keypoint_json output/"
        self.buttonBack.config(state='disabled')
        self.buttonStart.config(text="Stop",command=self.stop_to_start)
        
        if(FIRST_ACCESS_START == True):
            os.chdir('openpose-master')
            FIRST_ACCESS_START = False            
            
        cap = cv2.VideoCapture(VIDEO_FILE_PATH)

        if not cap.isOpened(): 
            print("Could not open : " + os.path.basename(VIDEO_FILE_PATH))

        #Problem with video_to_frame rmb to change divide 2
        if 'cv2.cv' in sys.modules:
            self.length = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
        else:
            self.length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


        direct =  os.getcwd() + "/output"
        os.system("rm " + direct + "/*")
        
        self.p1 = Process(target = self.functionB)       
        self.p2 = Process(target = self.after(1, self.check_file))
        
        self.p1.start()
        self.p2.start()
        
        self.p1.join()
        self.p2.join()

    def stop_to_start(self):
        
        result = messagebox.askquestion("Stopping the process", "Do you confirm want to stop the process? Once you stop, you cannot resume.", icon='warning')
        if result == 'yes':
            self.p1.terminate()
            self.p2.terminate()
            self.quit_process()
            self.progress['value'] = 0
            self.progressLabel.config(text="")
            self.buttonBack.config(state='normal')
            self.buttonStart.config(text="Start",command=self.start)  
        
    def close_current_window(self):
        self.quit_process()
        self.controller.close_all_window()  
        
    def quit_process(self):
        
        split_cmd = self.cmd.split()

        for process in psutil.process_iter():
            if process.cmdline() == split_cmd:
                print('Process found. Terminating it.')
                process.terminate()
                break


class PageThree(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        instruction = Label(self, text="Output from video file", anchor="w")
        instruction.pack(fill="both", pady=(10, 5), padx=(10, 0))
        instruction.config(font=('Calibri',18))




        csv_dir = '/Users/thammingkeat/PycharmProjects/athlete_data.csv'


        predictions = nn.predict_badminton_strokes(csv_dir)
        strokes_percentage = nn.calc_percentage_strokes(predictions)
        figure,ax = nn.plot_predictions(strokes_percentage)
        playstyle = nn.calc_playstyle(strokes_percentage)

        canvas = FigureCanvasTkAgg(figure, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=LEFT, fill=tk.BOTH, expand=False)
        #canvas.get_tk_widget().grid(row=1,column=0)

        percentages = 'Percentages of strokes used:' + '\n'
        percentages += 'Smash : ' + str(round(strokes_percentage[0],2)) + '\n'
        percentages += 'Lift : ' + str(round(strokes_percentage[1],2)) + '\n'
        percentages += 'Net : ' + str(round(strokes_percentage[2],2)) + '\n'
        percentages += 'Drive : ' + str(round(strokes_percentage[3],2)) + '\n'
        percentages += 'Serve: ' + str(round(strokes_percentage[4],2)) + '\n'
        percentages += 'Playstyle : ' + playstyle
        percentages = Label(self, text=percentages, anchor="w")
        percentages.pack(padx=(10,50), pady=(10,0), side=LEFT)


if __name__ == "__main__":
    global_paths()
    app = SampleApp()
    app.mainloop()