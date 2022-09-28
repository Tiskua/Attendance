import time
import tkinter as tk


from tkinter import filedialog
from tkinter import messagebox
from files import *

from tkinter import CENTER, RAISED, SUNKEN, Image, Toplevel
from tkinter.font import BOLD
from PIL import ImageTk, Image
from threading import Thread        
from datetime import date


from sheets import *
sheetclass = sheet()

class GUIS:
    def __init__(self):
        self.root = tk.Tk()
        self.BACKGROUND_COLOR = "burlywood1"
        self.BORDER_COLOR = "burlywood4"
        self.config = Files()

        self.selected_day = '1'
        self.selected_period = 1
        self.version = 1.0
        
    def open_Main_GUI(self):
        
        self.root.title('Select Options')
        self.root.resizable(False, False)
        
        canvas = tk.Canvas(self.root, height=600, width=600, bg=self.BACKGROUND_COLOR, highlightthickness = 10, highlightbackground =self.BORDER_COLOR)
        canvas.pack()

        select_period_label = tk.Label(canvas, text="Select which Period:",bg=self.BACKGROUND_COLOR)
        select_period_label.config(font=('helvetica', 10, BOLD))
        select_period_label.place(relx=0.5,rely=0.35, anchor=CENTER)

        if str(self.config.getLastRanTime()) != str(date.today().strftime("%d")):
            self.config.clearAbsentFile()
        self.config.setLastRanTime()

        self.config.writeVersion(self.version)
        
        PERIOD_OPTIONS = [period.strip() for period in self.config.getPeriodList().split(',')] 

        self.selected_period = tk.StringVar(canvas)
        self.selected_period.set(PERIOD_OPTIONS[0]) # default value

        period_options = tk.OptionMenu(canvas, self.selected_period, *PERIOD_OPTIONS)
        period_options["highlightthickness"]=0
        period_options.place(relx=0.5,rely=0.41,width=180,height=30, anchor=CENTER)


        select_day_label = tk.Label(canvas, text="Select which Day:",bg=self.BACKGROUND_COLOR)
        select_day_label.config(font=('helvetica', 10, BOLD))
        select_day_label.place(relx=0.5,rely=0.47, anchor=CENTER)

        DAY_OPTIONS = [
            "Day 1",
            "Day 2"
        ]

        self.selected_day = tk.StringVar(canvas)
        self.selected_day.set(DAY_OPTIONS[0]) # default value

        day_options = tk.OptionMenu(canvas, self.selected_day, *DAY_OPTIONS)
        day_options["highlightthickness"]=0
        day_options.place(relx=0.5,rely=0.53,width=180,height=30, anchor=CENTER)

        absent_sheet_error = tk.Label(canvas, text="", bg=self.BACKGROUND_COLOR, fg="red")
        absent_sheet_error.config(font=('helvetica', 10, BOLD))
        absent_sheet_error.place(relx=0.5, rely=0.68,anchor=CENTER)
        def go_command():
            
            sheetclass.getAbsentFile()
            if len(sheetclass.absent_students) == 0:
                absent_sheet_error['text'] = "Please Select An Absent Sheet!"
                return
            sheetclass.getStudents()
            p = self.selected_period.get().split(" ")[1]
            d = self.selected_day.get().split(" ")[1]

            sheetclass.getFormData(self.config.getPeriodSheetName(p), self.config.getPeriodSheetID(p), p, d)
            self.open_Attendence_GUI()  

        go_button = tk.Button(canvas, bg=self.BORDER_COLOR,padx=10,pady=1, text="Get Attendance", command=go_command, activebackground=self.BACKGROUND_COLOR)
        go_button.place(relx=0.5,rely=0.62, anchor=CENTER)

        settings_image = Image.open('settings_icon.png')
        resized = settings_image.resize((30,30), Image.Resampling.LANCZOS)
        final_settings_image = ImageTk.PhotoImage(resized)

        settings_button = tk.Button(canvas, bg=self.BACKGROUND_COLOR, image=final_settings_image, command=self.open_Settings_GUI, borderwidth=0, activebackground=self.BORDER_COLOR)
        settings_button.place(relx=0.93,rely=0.07,width=50,height=50, anchor=CENTER)

        loading = tk.Label(canvas,text="Scanning PDF File...",bg=self.BACKGROUND_COLOR)
        def showLoading():
            loading.config(text="Scanning PDF File...")
            loading.config(font=('helvetica', 10, BOLD))
            loading.place(relx=0.5,rely=0.72, anchor=CENTER)

        def showFinished():
            loading.config(text="Finished Scanning PDF File!")
            time.sleep(2)
            loading.config(text="")

        def open():
            absent_sheet_error['text'] = ""
            absent_file = filedialog.askopenfilename(initialdir="/Desktop", title="Select Absent Sheet", filetypes=(("pdf files", "*.pdf"),("all files", "*.*")))
            if(absent_file == ""): return
            showLoading()
            if not absent_file.endswith(".pdf"): 
                loading['text'] = ""
                absent_sheet_error['text'] = "The File must be a PDF"
                return
            
            if not sheetclass.setAbsentFile(absent_file):
                absent_sheet_error['text'] = "APIS are missing or invalid to read the File!"
                loading['text'] = ""
                return

            sheetclass.getAbsentFile()
            select_absent_file_button['text'] = 'A File is Selected'
            showFinished()
            return

        select_absent_file_button = tk.Button(canvas, text="Select Absent Sheet", command=lambda: Thread(target=open, daemon=True).start(), bg=self.BORDER_COLOR, activebackground=self.BACKGROUND_COLOR)
        select_absent_file_button.place(relx=0.13, rely=0.08, height=25,width=120, anchor=CENTER)

        if sheetclass.getAbsentFile(): select_absent_file_button['text'] = 'A File is Selected!'

        if self.config.updateAviable(): self.showUpdateGUI(True)
        
        if not sheetclass.setKeyFile():
            messagebox.showerror("Error","key.json file is invalid or missing!")
        self.root.mainloop()

    def showUpdateGUI(self, needToUpdate):
        update_window = tk.Toplevel(self.root)
        update_window.resizable=(False,False)
        update_window.title("Update")

        update_canvas = tk.Canvas(update_window, height=100, width=350, bg=self.BACKGROUND_COLOR, highlightthickness = 10, highlightbackground = self.BORDER_COLOR)
        update_canvas.pack()

        if needToUpdate:
            def openDownload():
                if self.config.downloadNewVersion(): pass
                else: messagebox.showerror("Error", "There was an error trying to Download the Update!")
                
            version = tk.Button(update_canvas, text="An update is available! Click to Download!",padx=5,pady=2, bg=self.BORDER_COLOR, command=openDownload)
            version.config(font=('helvetica', 10, BOLD))
            version.place(relx=0.5,rely=0.5, anchor=CENTER)
        else:
            version = tk.Label(update_canvas, text="You are Running the Latest Version!",padx=5,pady=2, bg=self.BACKGROUND_COLOR)
            version.config(font=('helvetica', 10, BOLD))
            version.place(relx=0.5,rely=0.5, anchor=CENTER)

    def open_Settings_GUI(self):
        sheetclass.sheets_list.clear()
        sheetclass.add_active_sheets()
        BUTTON_COLOR = "navy"
        BUTTON_TEXT_COLOR = "white"
        settings_window = Toplevel(self.root)
        settings_window.title("Settings")

        canvas = tk.Canvas(settings_window, height=800, width=800, bg=self.BACKGROUND_COLOR, highlightthickness = 10, highlightbackground = self.BORDER_COLOR)
        canvas.pack(fill=tk.BOTH, expand=True)

        sheet_settings_title = tk.Label(settings_window, text="Sheet Settings: ",bg=self.BACKGROUND_COLOR)
        sheet_settings_title.config(font=('helvetica', 20, BOLD))
        sheet_settings_title.place(relx=0.03,rely=0.03)

        spreadsheet_link_label = tk.Label(settings_window, text="Google Spreadsheet Link: " ,bg=self.BACKGROUND_COLOR)
        spreadsheet_link_label.config(font=('helvetica', 10, BOLD))
        spreadsheet_link_label.place(relx=0.03,rely=0.08)

        spreadsheet_link_text = tk.Text(settings_window)
        spreadsheet_link_text.place(relx=0.24,rely=0.08, height=20, width=520)
        spreadsheet_link_text.insert(tk.END, self.config.getSpreadSheetLink())

        def update_link():
            self.config.writeSpreadSheetLink(spreadsheet_link_text.get(1.0, tk.END))
            spreadsheet_ID_label['text'] = "Google Spreadsheet ID:" + self.config.getSpreadSheetID()
            settings_window.destroy()
            self.open_Settings_GUI()

        spreadsheet_link_update_button = tk.Button(settings_window, text="Update", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, pady=10, command=update_link)
        spreadsheet_link_update_button.place(relx=0.89,rely=0.08,height=20,width=70)

        spreadsheet_ID_label = tk.Label(settings_window, text="Google Spreadsheet ID: " + self.config.getSpreadSheetID() ,bg=self.BACKGROUND_COLOR)
        spreadsheet_ID_label.config(font=('helvetica', 10, BOLD))
        spreadsheet_ID_label.place(relx=0.03,rely=0.11)

        period_settings_title = tk.Label(settings_window, text="Period Settings: ",bg=self.BACKGROUND_COLOR)
        period_settings_title.config(font=('helvetica', 20, BOLD))
        period_settings_title.place(relx=0.03,rely=0.2)
        
        xpos = 0.04
        ypos = 0.25
        
        x= 0
        row_count = 0

        period_button_arr = []

        def show_period_info(period, button_num):
            global selected_period_num
            
            form_name_label['text'] = "Form Name: " + self.config.getPeriodSheetName(period)
            form_ID_label['text'] = "Form ID: " + self.config.getPeriodSheetID(period)

            for b in period_button_arr: b.config(bg=self.BORDER_COLOR, relief=RAISED)

            period_button_arr[button_num].config(bg=self.BACKGROUND_COLOR, relief=SUNKEN)
            selected_period_num = button_num

            sheet.set(SHEET_OPTIONS[0])
            for i in range(len(SHEET_OPTIONS)):
                if SHEET_OPTIONS[i] in form_name_label['text']: sheet.set(SHEET_OPTIONS[i]) 

        
        for period in self.config.getPeriodList().split(','):
            period_num = period.strip().split(" ")[1]
            button = tk.Button(settings_window, text=period, relief=RAISED, bg =self.BORDER_COLOR, command=lambda period_num=period_num, x=x: show_period_info(period_num, x))
            period_button_arr.append(button)

            row_count+=1
            if(row_count > 4):
                ypos += 0.025
                xpos = 0.04
                row_count = 1
            button.place(relx=xpos, rely=ypos, width=150, height=20)
            if x==0: button.config(bg=self.BACKGROUND_COLOR)
            xpos += 0.21
            x+=1
        
        def edit_period_list():
            edit_window = tk.Toplevel(self.root)
            edit_window.resizable=(False,False)
            edit_window.title("Settings")
            
            edit_canvas = tk.Canvas(edit_window, height=150, width=500, bg=self.BACKGROUND_COLOR, highlightthickness = 10, highlightbackground = self.BORDER_COLOR)
            edit_canvas.pack()

            period_list_text = tk.Text(edit_canvas)
            period_list_text.place(relx=0.5,rely=0.45,anchor=CENTER, width=470, height=50)
            period_list_text.insert(tk.END, str(self.config.getPeriodList()))

            def ok():
                self.config.writePeriodList(period_list_text.get(1.0,tk.END))
                edit_window.destroy()
                settings_window.destroy()
                self.open_Settings_GUI()
                
            ok_button = tk.Button(edit_canvas, text="Ok",bg=BUTTON_COLOR,fg=BUTTON_TEXT_COLOR, command=ok)
            ok_button.place(relx=0.5,rely=0.7,width=130,height=25,anchor=CENTER)


        edit_periods_button = tk.Button(settings_window, text="Edit", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=edit_period_list)
        edit_periods_button.place(relx=0.89,rely=0.25, width=60, height=20)

        first_period = self.config.getPeriodList().split(',')[0]

        form_name_label = tk.Label(settings_window, text="Form Name: " + self.config.getPeriodSheetName(first_period.split(" ")[1]), bg=self.BACKGROUND_COLOR)
        form_name_label.config(font=('helvetica', 10, BOLD))
        form_name_label.place(relx=0.04,rely=ypos+0.045)

        form_ID_label = tk.Label(settings_window, text="Form ID: " + self.config.getPeriodSheetID(first_period.split(" ")[1]), bg=self.BACKGROUND_COLOR)
        form_ID_label.config(font=('helvetica', 10, BOLD))
        form_ID_label.place(relx=0.04,rely=ypos+0.07)


        def updateSheetInfo():
            id = 000000000

            for info in sheetclass.sheets_list:
                if(info['title'] == sheet.get()): id = info["ID"]

            form_name_label['text'] = "Form Name: " + sheet.get()
            form_ID_label['text'] = "Form ID: " + str(id)
            
            try:
                config_period = period_button_arr[selected_period_num]['text'].strip().split(" ")[1]
            except: 
                config_period = period_button_arr[0]['text'].strip().split(" ")[1]

            self.config.checkPeriodConfigInfo(period)
            self.config.setPeriodSheetName(config_period, sheet.get())
            self.config.setPeriodSheetID(config_period, id)

        SHEET_OPTIONS = [info['title'] for info in sheetclass.sheets_list]
        sheet = tk.StringVar(canvas)
        
        sheet.set(SHEET_OPTIONS[0]) # default value
        for i in range(len(SHEET_OPTIONS)):
            if SHEET_OPTIONS[i] in form_name_label['text']: sheet.set(SHEET_OPTIONS[i]) 

        sheet_options = tk.OptionMenu(settings_window, sheet, *SHEET_OPTIONS)
        sheet_options["highlightthickness"]=0
        sheet_options.config(bg="gray95")
        sheet_options['menu'].config(bg='white')
        sheet_options.place(relx=0.04,rely=ypos+0.1,width=180,height=30)

        sheet_options_update_button = tk.Button(settings_window, text="Apply", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR,padx=10, pady=5, command= updateSheetInfo)
        sheet_options_update_button.place(relx=0.045,rely=ypos+0.14,height=20)

        students_settings_title = tk.Label(settings_window, text="Student Settings: ",bg=self.BACKGROUND_COLOR)
        students_settings_title.config(font=('helvetica', 20, BOLD))
        students_settings_title.place(relx=0.04,rely=ypos+0.2)

        edit_student_first_name_label = tk.Label(settings_window, text="First Name", bg=self.BACKGROUND_COLOR)
        edit_student_first_name_label.config(font=('helvetica', 10, BOLD))
        edit_student_first_name_label.place(relx=0.04, rely=ypos+0.26)
        edit_student_first_name_input = tk.Entry(settings_window)
        edit_student_first_name_input.place(relx=0.15, rely=ypos+0.26, width=200, height=20)

        edit_student_last_name_label = tk.Label(settings_window, text="Last Name", bg=self.BACKGROUND_COLOR)
        edit_student_last_name_label.config(font=('helvetica', 10, BOLD))
        edit_student_last_name_label.place(relx=0.04, rely=ypos+0.29)
        edit_student_last_name_input = tk.Entry(settings_window)
        edit_student_last_name_input.place(relx=0.15, rely=ypos+0.29, width=200, height=20)

        edit_student_period_label = tk.Label(settings_window, text="Period", bg=self.BACKGROUND_COLOR)
        edit_student_period_label.config(font=('helvetica', 10, BOLD))
        edit_student_period_label.place(relx=0.04, rely=ypos+0.32)
        edit_student_period_input = tk.Entry(settings_window)
        edit_student_period_input.place(relx=0.15, rely=ypos+0.32, width=200, height=20)

        edit_student_day_label = tk.Label(settings_window, text="Day", bg=self.BACKGROUND_COLOR)
        edit_student_day_label.config(font=('helvetica', 10, BOLD))
        edit_student_day_label.place(relx=0.04, rely=ypos+0.35)
        edit_student_day_input = tk.Entry(settings_window)
        edit_student_day_input.place(relx=0.15, rely=ypos+0.35, width=200, height=20)

        def validInputs():
            if(len(edit_student_first_name_input.get().strip(" ")) == 0 or len(edit_student_last_name_input.get().strip(" ")) == 0 
                or len(edit_student_period_input.get().strip(" ")) == 0 or len(edit_student_day_input.get().strip(" ")) == 0):
                result_message['text'] = "Please fill in all Fields!"
                return False
            return True

        def add_student():
            if not validInputs(): return         
            first_name = edit_student_first_name_input.get().lower().capitalize()
            last_name = edit_student_last_name_input.get().lower().capitalize()
            period = edit_student_period_input.get() 
            day = edit_student_day_input.get().replace("-","")
            with open("students.txt", "r") as f:
                student = first_name + ", " + last_name + " : " + period + " : " + day
                lines = f.readlines()
                for line in lines:
                    if line.strip("\n") == student:
                        result_message.config(fg='red')
                        result_message['text'] = "There is Already a Student in that Class!"
                        return

            file = open("students.txt", "a")
            
            file.write("\n" + first_name + ", " + last_name + " : " + period + " : " + day)
            result_message.config(fg='green')
            result_message['text'] = "Added " + first_name + " " + last_name + " to Period: " + period + " Day: " + day
            file.close()
        
        def remove_student():
            if not validInputs(): return

            first_name = edit_student_first_name_input.get().lower().capitalize()
            last_name = edit_student_last_name_input.get().lower().capitalize()
            period = edit_student_period_input.get() 
            day = edit_student_day_input.get().replace("-","")

            student = first_name + ", " + last_name + " : " + period + " : " + day

            foundStudent = False
            with open("students.txt", "r") as f:
                lines = f.readlines()

            with open("students.txt", "w") as f:
                for line in lines:
                    if line.strip("\n") != student: f.write(line)
                    else:
                        foundStudent = True
                        result_message.config(fg='green')
                        result_message['text'] = "Removed " + first_name + " " + last_name + " from Period: " + period + " Day: " + day
            
            if not foundStudent: 
                result_message.config(fg='red')
                result_message['text'] = "No Student was Removed!"

        def find_student():
            first_name = edit_student_first_name_input.get().lower()
            last_name = edit_student_last_name_input.get().lower()

            if len(first_name.strip(" ")) == 0 or len(last_name.strip(" ")) == 0 :
                result_message['text'] = "Please fill in First Name and Last Name Fields!"
                return 

            foundStudent = False
            with open("students.txt", "r") as f:
                lines = f.readlines()
                inClasses = []
                for line in lines:
                    if first_name in line.strip("\n").lower() and last_name in line.strip("\n").lower():
                        period = line.strip("\n").split(":")[1]
                        day = line.strip("\n").split(":")[2]
                        inClasses.append(first_name.capitalize() + " " + last_name.capitalize() + " is in Period: " + period + " Day: " + day)
                        foundStudent = True

            if not foundStudent: 
                result_message.config(fg='red')
                result_message['text'] = "No Student was Found!"
                return
            
            message = ""
            for c in inClasses: message += c +"\n "

            result_message.config(fg='green')
            result_message['text'] = message
           
                
        add_student_button = tk.Button(settings_window, text="Add the Student",command=add_student, bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, padx=3)
        add_student_button.place(relx=0.04,rely=ypos+0.4,width=110,height=25)

        remove_student_button = tk.Button(settings_window, text="Remove the Student", command=remove_student, bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, padx=3)
        remove_student_button.place(relx=0.23,rely=ypos+0.4,height=25)

        find_student_button = tk.Button(settings_window, text="Find the Student", command=find_student, bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, padx=3)
        find_student_button.place(relx=0.43,rely=ypos+0.4,height=25)

        result_message = tk.Label(settings_window, text="", bg=self.BACKGROUND_COLOR, justify=tk.RIGHT)
        result_message.config(font=('helvetica', 10, BOLD), fg='red')
        result_message.place(relx=0.04,rely=ypos+0.45)

        version_label = tk.Label(settings_window, text="version: " + self.config.getUserVersion(), bg=self.BACKGROUND_COLOR)
        version_label.config(font=('helvetica', 9, BOLD))
        version_label.place(relx=0.89,rely=0.95)

        def checkForUpdate():
            self.showUpdateGUI(self.config.updateAviable())

        update_button = tk.Button(settings_window, text="Check For Update", bg=BUTTON_COLOR, fg=BUTTON_TEXT_COLOR, command=lambda: checkForUpdate())
        update_button.config(font=('helvetica', 9))
        update_button.place(relx=0.74,rely=0.95, height=25)


    def open_Attendence_GUI(self):
        attendance_window = Toplevel(self.root)
        attendance_window.title("Attendance")

        canvas = tk.Canvas(attendance_window, height=750, width=1000, bg=self.BACKGROUND_COLOR, highlightthickness = 10, highlightbackground = self.BORDER_COLOR)
        canvas.pack(fil=tk.BOTH, expand=True)

        def showAttendance():
            list_sorted_by_last = sorted(sheetclass.students_attendance, key=lambda d: d['last_name'].lower())

            total_count = 0

            present_count = 0
            absent_count = 0
            wrong_count = 0
            missing_count = 0
            late_count = 0

            x_pos = 0.02
            y_pos = 0.08

            row_gap = 0.03
            column_gap = 0.18

            attendance_window.update()
            rows_per_column = attendance_window.winfo_height()//28
            
            row_num = 0

            for student in list_sorted_by_last:
                
                if(student['period'].strip() != self.selected_period.get().split(" ")[1].strip()):continue
                if(int(student['day']) != int(self.selected_day.get().split(" ")[1]) and int(student['day']) != 12): continue

                total_count+=1
                student_label = tk.Label(attendance_window, text=student['last_name'] + ", " + student['first_name'])
                student_label.config(font=('helvetica', 9, BOLD))

                if(student['attendance'] == "PRESENT"):
                    student_label.config(bg="spring green")
                    present_count +=1
                elif(student['attendance'] == "ABSENT"):
                    student_label.config(bg="tomato")
                    absent_count +=1
                elif(student['attendance'] == "WRONG"):
                    student_label.config(bg="orange")
                    wrong_count +=1
                elif(student['attendance'] == "MISSING"):
                    student_label.config(bg="dodger blue")
                    missing_count +=1
                elif(student['attendance'] == "LATE"):
                    student_label.config(bg="purple1")
                    late_count +=1
                
                student_label.place(relx=x_pos,rely=y_pos,width=170)

                y_pos += row_gap
                row_num +=1

                if(row_num > rows_per_column):
                    x_pos += column_gap
                    row_num = 0
                    y_pos = 0.08
            total_num_label = tk.Label(attendance_window, text="Total: " + str(total_count), bg=self.BACKGROUND_COLOR)
            total_num_label.config(font=('helvetica', 15, BOLD))
            total_num_label.place(x=70,rely=0.05, anchor=CENTER)

            present_num_label = tk.Label(attendance_window, text="Present: " + str(present_count), bg=self.BACKGROUND_COLOR,highlightbackground="spring green", highlightthickness=2)
            present_num_label.config(font=('helvetica', 8, BOLD))
            present_num_label.place(relx=0.1,rely=0.96, anchor=CENTER)

            absent_num_label = tk.Label(attendance_window, text="Absent: " + str(absent_count), bg=self.BACKGROUND_COLOR,highlightbackground="tomato", highlightthickness=2)
            absent_num_label.config(font=('helvetica', 8, BOLD))
            absent_num_label.place(relx=0.3,rely=0.96, anchor=CENTER)

            wrong_num_label = tk.Label(attendance_window, text="Wrong: " + str(wrong_count), bg=self.BACKGROUND_COLOR, highlightbackground="orange", highlightthickness=2)
            wrong_num_label.config(font=('helvetica', 8, BOLD))
            wrong_num_label.place(relx=0.5,rely=0.96, anchor=CENTER)

            late_num_label = tk.Label(attendance_window, text="Late: " + str(late_count), bg=self.BACKGROUND_COLOR,highlightbackground="purple1", highlightthickness=2)
            late_num_label.config(font=('helvetica', 8, BOLD))
            late_num_label.place(relx=0.7,rely=0.96, anchor=CENTER)

            missing_num_label = tk.Label(attendance_window, text="Missing: " + str(missing_count), bg=self.BACKGROUND_COLOR,highlightbackground="dodger blue", highlightthickness=2)
            missing_num_label.config(font=('helvetica', 8, BOLD))
            missing_num_label.place(relx=0.90,rely=0.96, anchor=CENTER)


        showAttendance()

guis = GUIS()
guis.open_Main_GUI()