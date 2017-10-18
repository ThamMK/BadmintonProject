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
from PIL import Image,ImageTk,ImageFile,ImageFont,ImageDraw
import numpy as np
import neural_network as nn
import read_pose_json as tool
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tryout import Player


def global_paths():

    global VIDEO_FILE_PATH
    global FIRST_ACCESS_START
    global WEBCAM_SELECTED
    global last_frame
    global should_continue_animating
    global should_continue_checkfile
    
    VIDEO_FILE_PATH = None
    FIRST_ACCESS_START = True
    WEBCAM_SELECTED = None
    last_frame = np.zeros((640, 480, 3), dtype=np.uint8)
    should_continue_animating = True
    should_continue_checkfile = True
    ImageFile.LOAD_TRUNCATED_IMAGES = True

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")
        self.body_font = tkfont.Font(family='Helvetica', size=10)
        
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=False)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, PageOne, PageTwo,PageThree,Webcam,RunWebcam,Player):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")
        
    def get_page(self, page_class):
        return self.frames[page_class]

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")
        
    def stop_all(self):
        
        #if x in locals() or x in globals():
        print("coming soon")
        
    def close_all_window(self):
        app.destroy()
        sys.exit()
        app.quit()

class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.image = Image.open(os.getcwd() + "/badminton.jpg")
        self.image = self.image.resize((540, 360), Image.ANTIALIAS) 
        self.img = ImageTk.PhotoImage(self.image)
        
        self.photoLabel = Label(self,image=self.img)
        self.photoLabel.pack()

        bottom = Frame(self)
        
        button1 = tk.Button(self, text="Video",width=19,command=lambda: controller.show_frame("PageOne"))
        button2 = tk.Button(self, text="Webcam",width=19,command=lambda: controller.show_frame("Webcam"))
        button3 = tk.Button(self, text="Quit",width=19,command=self.controller.close_all_window)
        
        button1.config(font=controller.body_font) 
        button2.config(font=controller.body_font)         
        button3.config(font=controller.body_font)         
        
        button1.pack(in_=bottom,side=LEFT)
        button2.pack(in_=bottom,side=LEFT)
        button3.pack(in_=bottom,side=LEFT)
        
        bottom.pack(fill=BOTH,side=BOTTOM,expand=False,padx=1)

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
        
        self.backB = Button(self,text="Back",width=10,command=lambda: controller.show_frame("StartPage"))
        self.backB.grid(row=2,column=1,sticky=E,pady=(20,5),padx=(35,0))
        
        self.nextB = Button(self,text="Next",width=10,command=self.check_file_valid)
        self.nextB.config(state='disabled')
        self.nextB.grid(row=2,column=2,sticky=E,pady=(20,5),padx=(0,4))
        
        cancelB = Button(self,text="Quit",width=10,command=self.controller.close_all_window)
        cancelB.grid(row=2,column=4,sticky=E,pady=(20,5),padx=(4,10))
        
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
        
        self.buttonStart = Button(self,text="Start",width=10,command=self.start)
        self.buttonStart.pack(in_ = center, padx=(0,10),side=RIGHT)
        
        center.pack(fill=BOTH,pady=(10,0))
        
        horizontal_line = ttk.Separator(self,orient=HORIZONTAL)
        horizontal_line.pack(pady = (15,5),padx = (10,10),fill=BOTH)
        
        bottom = Frame(self)
        
        buttonQuit= Button(self,text="Quit",width=10,command=self.close_current_window)
        buttonQuit.pack(in_=bottom,side=RIGHT,padx = (0,10))
        
        self.buttonNext= Button(self,text="Next",width=10,command=lambda: controller.show_frame("PageThree"))
        self.buttonNext.pack(in_=bottom,side=RIGHT,padx = (0,10))
        self.buttonNext.config(state='disabled')
        
        self.buttonBack= Button(self,text="Back",width=10,command=lambda: controller.show_frame("PageOne"))
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
        number_files = len(list) / 2 #Divided by 2 because got 2 outputs - json and img
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
        
        self.cmd = "./build/examples/openpose/openpose.bin --video " + VIDEO_FILE_PATH +" --no_display --write_keypoint_json output/ --write_images output/ --keypoint_scale 2"
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

        self.bind("<<ShowFrame>>", self.onShowFrame)

    def onShowFrame(self, event):

        json_dir = os.getcwd() + "/output"
        img_dir = os.getcwd() + "/output"
        csv_dir = os.pardir + "/athlete_data.csv"
        folder_people, folder_bb, list_people, list_bb = tool.read_json(json_dir)
        tool.draw_bounding_box(img_dir,list_bb)
        list_people = tool.adjust_coordinates(list_people)
        tool.write_to_csv(csv_dir, list_people)

        x = [0,1,2,3,4,5]
        strokes_xticks = ['Smash','Lift', 'Net', 'Drive', 'Serve']



        predictions = nn.predict_badminton_strokes(csv_dir)
        strokes_percentage = nn.calc_percentage_strokes(predictions)
        figure,ax = nn.plot_predictions(strokes_percentage)
        playstyle = nn.calc_playstyle(strokes_percentage)

        tool.draw_prediction(img_dir,predictions)
       
        canvas = FigureCanvasTkAgg(figure, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=LEFT, fill=tk.BOTH, expand=False)
        

        percentages = 'Percentages of strokes used:' + '\n'
        percentages += 'Smash : ' + str(round(strokes_percentage[0],2)) + '\n'
        percentages += 'Lift : ' + str(round(strokes_percentage[1],2)) + '\n'
        percentages += 'Net : ' + str(round(strokes_percentage[2],2)) + '\n'
        percentages += 'Drive : ' + str(round(strokes_percentage[3],2)) + '\n'
        percentages += 'Serve: ' + str(round(strokes_percentage[4],2)) + '\n'
        percentages += 'Playstyle : ' + playstyle
        percentages = Label(self, text=percentages, anchor="w")
        percentages.pack(padx=(10,50), pady=(10,0), side=LEFT)
            
                    
            
            
class Webcam(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.camera_selected = ""
        
        instruction = Label(self,text="Please select one camera device.",anchor="w")
        instruction.pack(fill="both",pady = (10,0),padx = (10,0))
        instruction.config(font=controller.body_font)      
        
        left = Frame(self)
        self.webcamLB = Listbox(left,selectmode=EXTENDED,height=5,width=45)
        list_webcam = self.search_webcam()
        
        for i in range(len(list_webcam)):
            self.webcamLB.insert(list_webcam[i][1],list_webcam[i][0])

        self.webcamLB.config(font=controller.body_font)         
        self.webcamLB.pack()
        left.pack(fill=BOTH,side=LEFT,padx=(10,0),pady=(5,0))
        
        selectButton = Button(self,text="Select",command=self.select_webcam)
        selectButton.pack(fill=BOTH,padx=5,pady=(5,0))
        
        backButton = Button(self,text="Back",command=lambda: controller.show_frame("StartPage"))
        backButton.pack(fill=BOTH,padx=5,pady=5)
        
    def search_webcam(self):
        p = subprocess.Popen('v4l2-ctl --list-devices', stdout=subprocess.PIPE,shell=True, preexec_fn=os.setsid) 
        output, errors = p.communicate()
        lines = output.splitlines()
        list_webcam = []
        
        for i in range (len(lines)/3):
            webcam = lines[i*3]
            webcam_id = lines[i*3+1]
            webcam = webcam.split("(")[0]
            webcam_id = webcam_id[-1:]
            webcam = (webcam,webcam_id)
            list_webcam.append(webcam)
            
        return list_webcam
        
    def select_webcam(self):
        selected = self.webcamLB.curselection()
        global should_continue_animating
        should_continue_animating = True
        
        print(selected)
        is_selected = None
        for item in selected:
            if(item is None):
                print(None)
            else:
                is_selected = item
        
        if(is_selected is not None):
            self.camera_selected = selected[0]
            global WEBCAM_SELECTED
            WEBCAM_SELECTED = str(self.camera_selected)
            pageRunWebcam = self.controller.get_page("RunWebcam")
            pageRunWebcam.run()
            self.controller.show_frame("RunWebcam")
        else:
            messagebox.showerror("No device is selected","No camera device is selected. Please select a device to continue.")
            print("Nothing is selected")
#        for i in selected:
#            print(self.webcamLB.get(i))

class RunWebcam(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def run(self):
        pageWebcam = self.controller.get_page("Webcam")
        camera_selected = pageWebcam.camera_selected

        self.cam = cv2.VideoCapture(camera_selected)

        self.video_webcam = Label(self)
        self.video_webcam.pack()

        self.bottom = Frame(self)

        self.buttonStart = Button(self, text="Start", width=8, command=self.start)
        self.buttonStart.pack(in_=self.bottom, side=LEFT)

        self.buttonBack = Button(self, text="Back", width=8, command=self.back_to_previous)
        self.buttonBack.pack(in_=self.bottom, side=LEFT)

        self.bottom.pack(side=BOTTOM)

        self.start_frame()

    def start(self):
        global FIRST_ACCESS_START
        global WEBCAM_SELECTED

        if (WEBCAM_SELECTED is not None):
            camera_selected = WEBCAM_SELECTED
            print(camera_selected)

            self.buttonStart.config(text="Stop", command=self.stop_to_start)
            self.buttonBack.config(state='disabled')

            self.cmd = "./build/examples/openpose/openpose.bin --camera " + camera_selected + " --write_images output/ --write_keypoint_json output/ --no_display"

            self.stop_webcam()
            self.video_webcam.configure(image='', text="Loading..")

            if (FIRST_ACCESS_START == True):
                os.chdir('openpose-master')
                FIRST_ACCESS_START = False

            direct = os.getcwd() + "/output"
            os.system("rm " + direct + "/*")

            self.p1 = Process(target=self.openpose_webcam)
            self.p2 = Process(target=self.process_images_openpsoe(direct))

            self.p1.start()
            self.p2.start()

    def openpose_webcam(self):

        # os.system(cmd)
        subprocess.Popen(self.cmd, stdout=subprocess.PIPE, shell=True, preexec_fn=os.setsid)

    def stop_to_start(self):
        result = messagebox.askquestion("Stopping the process",
                                        "Do you confirm want to stop the process? Once you stop, you cannot resume.",
                                        icon='warning')
        if result == 'yes':
            self.p1.terminate()
            self.p2.terminate()
            self.stop_checkfile()
            self.quit_process()
            self.buttonBack.config(state='normal')
            self.buttonStart.config(text="Start", command=self.start)
            self.controller.show_frame("Player")

    def quit_process(self):

        split_cmd = self.cmd.split()

        for process in psutil.process_iter():
            if process.cmdline() == split_cmd:
                print('Process found. Terminating it.')
                process.terminate()
                break

    def start_frame(self):
        flag, frame = self.cam.read()
        frame = cv2.flip(frame, 1)
        if flag is None:
            print "Major error!"
            #        <code to handle exception>
        elif flag:
            global last_frame
            last_frame = frame.copy()
            cv2image = cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGBA)
            img = Image.fromarray(cv2image)
            img = img.resize((540, 360), Image.ANTIALIAS)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_webcam.imgtk = imgtk
            self.video_webcam.configure(image=imgtk)
        else:
            print "Cant process the image"
            #        <code to handle exception>

        if should_continue_animating:
            self.video_webcam.after(10, self.start_frame)

    def stop_webcam(self):
        global should_continue_animating
        should_continue_animating = False
        self.cam.release()

    def back_to_previous(self):

        global FIRST_ACCESS_START
        if (FIRST_ACCESS_START == False):
            os.chdir('..')
            FIRST_ACCESS_START = True
        self.stop_webcam()
        self.video_webcam.pack_forget()
        self.bottom.pack_forget()
        self.controller.show_frame("Webcam")

    def get_latest_image(self, dirpath, valid_extensions=('jpg', 'jpeg', 'png')):
        """
        Get the latest image file in the given directory
        """
        # get filepaths of all files and dirs in the given dir
        valid_files = [os.path.join(dirpath, filename) for filename in os.listdir(str(dirpath))]

        # filter out directories, no-extension, and wrong extension files
        valid_files = [f for f in valid_files if '.' in f and \
                       f.rsplit('.', 1)[-1] in valid_extensions and os.path.isfile(f)]

        if (len(valid_files) == 0):
            print("No valid images in %s" % dirpath)
            return None
        else:
            return max(valid_files, key=os.path.getmtime)

    def process_images_openpsoe(self, direct):

        latest_image_path = self.get_latest_image(direct)

        if (latest_image_path is not None):
            try:
                self.image = Image.open(latest_image_path)

                font = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 40)
                self.image = self.image.resize((540, 360), Image.ANTIALIAS)
                self.image = self.image.transpose(Image.FLIP_LEFT_RIGHT)

                draw = ImageDraw.Draw(self.image)
                draw.text(((0 + 10), (0 + 10)), "Smash", (255, 255, 0), font=font)
                draw = ImageDraw.Draw(self.image)

                self.img = ImageTk.PhotoImage(self.image)

                self.video_webcam.imgtk = self.img
                self.video_webcam.configure(image=self.img)

            except (IOError, SyntaxError):
                print('Bad file:', latest_image_path)  # print out the names of corrupt files

        if (should_continue_checkfile):
            self.after(600, self.process_images_openpsoe, direct)
        else:
            self.video_webcam.imgtk = ""
            self.video_webcam.configure(image="")
            global should_continue_checkfile
            should_continue_checkfile = True

    def stop_checkfile(self):
        global should_continue_checkfile
        should_continue_checkfile = False

if __name__ == "__main__":
    global_paths()
    app = SampleApp()
    app.mainloop()