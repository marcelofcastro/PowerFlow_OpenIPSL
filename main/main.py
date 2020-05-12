#================================================================================== 
# Code Part: Loading libraries     
# Author: marcelofcastro         
# Description: Loading libraries the whole system. Compatible with python 2. and 3.
#==================================================================================
try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter 
    import tkFileDialog
    import tkMessageBox
except ImportError:
    # for Python3
    from tkinter import *   ## notice lowercase 't' in tkinter here
    import tkinter.filedialog as tkFileDialog
    import tkinter.messagebox as tkMessageBox
#========================================================================== 
# Code Part: Function definition:  
# Author: marcelofcastro         
# Description: Definition of functions for reading files.
#========================================================================== 
def donothing():
    filewin = Toplevel(root)
    button = Button(filewin, text="Do nothing button")
    button.pack()
def readmo():
    filepath = tkFileDialog.askopenfilename()
    tkMessageBox.showinfo("File loaded", "The modelica file has been loaded.")
    Content = []
    with open(filepath,"r+") as input_file:
    	for line in input_file:
    		Content.append(line)
    input_file.close()
    for ii in range(0,len(Content),1):
        test_connect = Content[ii].find("equation")
        if test_connect == 0:
            index_eq = ii
    out_file = open("Teste.txt","w+") 
    out_file.write("\n Connection starts at line %f \n\n" % (float(index_eq)))    
#========================================================================== 
# Code Part: Graphical User Interface   
# Author: marcelofcastro          
# Description: Python GUI interface for OpenIPSL initialization software.
#==========================================================================  
root = Tk()
root.title("Model Translation Tool")
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Load", command=readmo)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)
helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="Help Index", command=donothing)
helpmenu.add_command(label="About...", command=donothing)
menubar.add_cascade(label="Help", menu=helpmenu)
root.config(menu=menubar)
root.mainloop()