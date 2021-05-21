#================================================================================== 
# Code Part: Loading libraries     
# Author: marcelofcastro         
# Description: Loading libraries the whole system. Compatible with python 2. and 3.
#==================================================================================
# ----- Importing Tkinter:
try:
    # for Python2
    from Tkinter import * ## notice capitalized T in Tkinter 
    from Tkinter import ttk
    from Tkinter import tkFileDialog
    from Tkinter import tkMessageBox
except ImportError:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here
    from tkinter import ttk
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as tkMessageBox
# ----- Importing sys module:
import sys, os, time
homedir= os.getcwd()
# ----- Adding paths for new modules:
srcdir = homedir + "/src"
auxdir = homedir + "/aux"
imgdir = homedir + "/img" # create img dir path
sys.path.insert(1, srcdir)
sys.path.insert(2, auxdir)
sys.path.insert(3, imgdir) # add img dir to home path
# ----- Importing auxiliary functions:
import directory_functions
import psse2mo
#==================================================================================
# Code Part: Functions for GUI 
# Author: marcelofcastro         
# Description: Definition of functions for reading files.
#==================================================================================
def donothing():
    filewin = Toplevel(root)
    button = Button(filewin, text="Do nothing button")
    button.pack()
def debug():
    print(srcdir)
    print(auxdir)
def frompsse():
    # ----- RAW file reader:
    rawfile = directory_functions.askRawfile() # ask the user which raw file will be translated
    start_readraw = time.time() # initial time for raw.
    [system_base,system_frequency,sysdata,psse_version] = psse2mo.readRaw(rawfile) # parse and format rawfile for sysdata
    time_readraw = time.time() - start_readraw # time for raw.
    # ----- DYR file reader:
    dyrfile = directory_functions.askDyrfile() # ask the user which dyr file will be translated
    start_readdyr = time.time() # initial time for dyr.
    dyrdata = psse2mo.readDyr(dyrfile)
    time_readdyr = time.time() - start_readdyr # time for dyr.
    # ----- Creating directories:
    userpath = directory_functions.askDir() # get directory where user wants files to be placed
    # ----- Translation to Modelica:
    start_trans = time.time() # initial time.
    [wdir,sdir,ddir,gdir] = directory_functions.createDir(userpath) # creates folders for placement of results   
    psse2mo.writeMo(wdir,sdir,ddir,gdir,system_base,system_frequency,sysdata,dyrdata) # writes models
    time_trans = time.time()- start_trans # calculate execution time
    # ----- Updating parameters and writing log:
    total_time = time_trans + time_readraw + time_readdyr
    times = [time_readraw,time_readdyr,time_trans,total_time]
    psse2mo.writeLog(wdir,system_base,system_frequency,psse_version,sysdata,dyrdata,times)
#==================================================================================
# Code Part: Graphical User Interface   
# Author: marcelofcastro          
# Description: Python GUI interface for model translation tool.
#==================================================================================  
root = Tk()
# ----- Root Frame:
root.title("Model Translation Tool")
root.geometry("350x800")


# ----- Right frame with additional info:
rightframe = Frame(master=root, width=400, height=800, bg="white")
rightframe.pack(side=RIGHT)

introtxt = "Model Translation Tool"
copytxt = "AlsetLab and New York Power Authority \n 2021"
canvas = Canvas(rightframe, width = 400, height = 800, bg="white")
canvas.pack(fill = BOTH, expand = True)
icon = PhotoImage(file = imgdir+'/icon.png')
icon = icon.zoom(4)
icon = icon.subsample(9)
canvas.create_image(190, 235, image=icon)
canvas.create_text(175, 50, text = introtxt, font = ('Times New Roman', 18), justify = 'center', fill='black')
canvas.create_text(175, 750, text = copytxt, font = ('Times New Roman', 12), justify = 'center', fill='black')
canvas.update

# ----- Left frame with text being displayed
# leftframe = Frame(master=root, width=1242, height=800, bg="white")
# leftframe.pack(side=LEFT)

# ----- Menu
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
newmenu = Menu(menubar,tearoff=0)
filemenu.add_cascade(label="New Translation", menu=newmenu)
newmenu.add_command(label="From PSS/E File",command = frompsse)
newmenu.add_command(label="From Modelica File",command = donothing)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Debug Function", command=debug)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)
root.config(menu=menubar)
root.mainloop()