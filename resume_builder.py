import os
import tkinter as tk
from tkinter import ttk
import db_main
from cs50 import SQL

#define database
db = SQL("sqlite:///jobsheet.db")

#populate database with key terms
if (db.execute("SELECT * FROM keywords") == None):
    db_main.exec_script("data.sql", db)

#app frame
# root = tk.Tk()
# root.geometry("1480x960")
# root.title("Resume Builder")

TITLE = ("Calibri", 25)

class tkinterApp(tk.Tk):
     
    # __init__ function for class tkinterApp
    def __init__(app, *args, **kwargs):
         
        # __init__ function for class Tk
        tk.Tk.__init__(app, *args, **kwargs)

        # creating a container
        container = tk.Frame(app) 
        container.pack(side = "top", fill = "both", expand = True)
  
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
  
        # initializing frames to an empty array
        app.frames = {} 
  
        # iterating through a tuple consisting of the different page layouts
        for F in (StartPage, Page1):
  
            frame = F(container, app)
  
            # initializing frame of that object from
            # startpage, page1 with for loop
            app.frames[F] = frame
  
            frame.grid(row = 0, column = 0, sticky ="nsew")
  
        app.show_frame(StartPage)
  
    # to display the current frame passed as
    # parameter
    def show_frame(app, cont):
        frame = app.frames[cont]
        frame.tkraise()
  
# first window frame startpage
  
class StartPage(tk.Frame):
    def __init__(app, parent, controller):
        tk.Frame.__init__(app, parent)
         
        instruct = ttk.Label(app, text= "Set up profile")
        instruct.grid(row=0, column=1 , padx=5, pady=5)

        #frame 1 for job input
        #input
        job = tk.StringVar()
        location = tk.StringVar()
        start_date=tk.StringVar()
        end_date=tk.StringVar()
        exp=tk.StringVar()
        # skill= tk.StringVar()
        # project= tk.StringVar() #add option to connect to job
        # project_desc= tk.StringVar()
        # startmonth= tk.StringVar()

        #job input fields
        link_0=ttk.Entry(app, width=50, textvariable=job)
        position = ttk.Label(app, text= "Job Title: ")

        #TODO: fix scaling
        link_1=ttk.Entry(app, width=50, textvariable=location)
        position1 = ttk.Label(app, text= "Location:")

        link_2=ttk.Entry(app, width=40, textvariable=start_date)
        position2 =  ttk.Label(app, text= "Start Date: ")

        link_3=ttk.Entry(app, width=40, textvariable=end_date)
        position3 =  ttk.Label(app, text= "End Date: ")
        #TODO: L/M change date input fields to drop downs.

        link_0.grid(row=1, column=1, padx=5, pady=5)
        position.grid(row=1, column=0, padx=5, pady=5)
        link_1.grid(row=1, column=3, padx=5, pady=5)
        position1.grid(row=1, column=2, padx=5, pady=5)
        link_2.grid(row=1, column=5, padx=5, pady=5)
        position2.grid(row=1, column=4, padx=5, pady=5)
        link_3.grid(row=1, column=7, padx=5, pady=5)
        position3.grid(row=1, column=6, padx=5, pady=5)

        #big experience input field
        add_experience = ttk.Entry(app, width=160, textvariable=exp)
        position4 =  ttk.Label(app, text= "Add experience, use action verbs: ")
        add_experience.grid(row=2, column=1, padx=5, pady=5, columnspan= 4)
        position4.grid(row=2, column=0, padx=5, pady=5)

        #button to add experiences
        exp_place = []
        try:
            exp_button = ttk.Button(app, text="Add", command= lambda: exp_place.append(exp.get()))
        except Exception as e:
            print("Error in db_main, exp:", e)

        exp_button.grid(row=2, column=5, padx=5, pady=5)

        # Define a function to handle the job addition
        def add_job():
            job_info = [job.get(), location.get(), start_date.get(), end_date.get()]
            db_main.add_job_history(job_info[0], job_info[1], job_info[2], exp_place, db)
            # Reset lists
            job_info.clear()
            exp_place.clear()
        
        #TODO: fix the scaling, have the input boxes reset, wrapi it up, presentation

        #button to add all that to db
        try:
            job_button = ttk.Button(app, text="Add Job", command= lambda: add_job())
            job_button.grid(row=3, column=2, padx=5, pady=5)       
        except Exception as e:
            print("Error in db_main, job:", e)

        
        #frame 2 for skills/projects input
        '''
        #smaller input fields for skills and projects
        add_skill=ttk.Entry(app, width=100, height= 40, placeholder_text="Skill", textvariable=skill)
        add_project=ttk.Entry(app, width=100, height= 40, placeholder_text="Project", textvariable=project)
        add_project_desc=ttk.Entry(app, width=100, height= 90, placeholder_text="Description of Project", textvariable=project_desc)
        add_skill.pack()
        add_project.pack()
        add_project_desc.pack()

        #add buttons
        project_button=ttk.Button(app, "Add Project", command=db_main.add_projects(project, project_desc))
        project_button.pack()

        skill_button=ttk.Button(app, "Add Skill", command=db_main.add_skills(skill))
        skill_button.pack()

        finish_button = ttk.Button(app, "Finished", command=switch())
        finish_button.pack()
        '''

        #outside frame to move to next page
        button1 = ttk.Button(app, text ="Craft Custom Job Features",
        command = lambda : controller.show_frame(Page1))

        # putting the button in its place by
        # using grid
        button1.grid(row = 5, column = 1, padx = 2, pady = 3)
  
# second window frame page1
class Page1(tk.Frame):
     
    def __init__(app, parent, controller):
         
        tk.Frame.__init__(app, parent)
        label = ttk.Label(app, text ="Build Job Application", font = TITLE)
        label.grid(row = 0, column = 2, padx = 4, pady = 4)
  
        # button to show frame 2 with text
        # layout2
        button1 = ttk.Button(app, text ="Add to Profile",
                            command = lambda : controller.show_frame(StartPage))
     
        # putting the button in its place
        # by using grid
        button1.grid(row = 1, column = 1, padx = 4, pady = 4)
        
        #Instruction
        instruct = ttk.Label(app, text= "Paste Job Description")
        instruct.grid(row=2, column=0, padx=5, pady=5)

        job_description= tk.StringVar()
        description=ttk.Entry(app, width=200, textvariable=job_description)
        description.grid(row=2, column=1, padx=5, pady=5)

        try:
            description_button=ttk.Button(app, text="Submit", command= lambda: db_main.output_resume(job_description, db))
            description_button.grid(row=3, column=1, padx=5, pady=5)
        except Exception as e:
            print("Error in db_main, full:", e)
        

#run app
if __name__ == "__main__":
    app = tkinterApp()
    app.mainloop()