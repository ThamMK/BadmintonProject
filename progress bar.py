
import Tkinter as tk
import ttk
import time
import os
import cv2
from multiprocessing import Process

class progress_bar(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        s = ttk.Style()
        s.theme_use('clam')
        s.configure("red.Horizontal.TProgressbar", foreground='red', background='red')
        self.progress = ttk.Progressbar(self, style="red.Horizontal.TProgressbar", orient="horizontal", length=500, mode="determinate")
        self.progress.pack()
        self.val = 0
        self.maxval = 1
        self.progress["maximum"] = 1

    def updating(self, val):
        self.val = val
        self.progress["value"] = self.val
        print(self.val)

        #should change to available for next button once it is finish
        #if self.val == self.maxval:
            #self.destroy()

def calculate_files():
    import os, os.path

    direct =  os.getcwd() + "/output"
    list = os.listdir(direct) # dir is your directory path
    number_files = len(list)
    print number_files
    return number_files

def test(i=calculate_files()):
    app.updating(i/ float(length))
    print(i/float(length))
    if(i/float(length) < 1.0):
        app.after(100, test, calculate_files())
        
def functionA():
    app.after(1, test)
    app.mainloop()
    
def functionB():
    #os.system('python video_to_frame.py')
    import subprocess,psutil,time
    cmd = "python video_to_frame.py"
    P = subprocess.Popen(cmd,shell=True)
    psProcess = psutil.Process(pid=P.pid)

cap = cv2.VideoCapture("video2.avi")

if not cap.isOpened(): 
    print("could not open : video2.avi")

#Problem with video_to_frame rmb to change divide 2
length = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))/2
print(length)

direct =  os.getcwd() + "/output"
os.system("rm " + direct + "/*")

app = progress_bar()

p1 = Process(target = functionB)
p1.start()

p2 = Process(target = functionA)
p2.start()

p1.join()
p2.join()














