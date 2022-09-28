from files import Files
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from datetime import datetime
from pdf2image import convert_from_path

import pytesseract 
import os

class sheet:
    def __init__(self):
        self.sheets_list = []
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.SERVICE_ACCOUNT_FILE = 'keys.json'
        self.creds = None
        self.setKeyFile()
        self.config = Files()
        self.students_attendance = []
        self.absent_students = []
        self.old_attendance = []


    def getStudents(self):
        file = open("students.txt", "r")
        lines = file.readlines()
        for line in lines:
            
            firstname = line.split(' ')[0].replace("\n", "").replace(",", "")
            lastname = line.split(' ')[1].replace("\n", "").replace(",", "")

            period = line.split(':')[1]
            day = line.split(':')[2]

            student_attendence = {
                    'first_name' : firstname,
                    'last_name' : lastname,
                    'attendance' : "MISSING",
                    "period" : period,
                    "day" : day
                }
            self.students_attendance.append(student_attendence)



    def getFormData(self, sheet_name, sheet_id, period, day):
        try:
            self.getAbsentStudents()
            service = build('sheets', 'v4', credentials=self.creds)
            SAMPLE_RANGE_NAME = sheet_name + "!A:C"
            SPREADSHEET_ID = self.config.getSpreadSheetID()
            
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()

            values = result.get('values', [])

            for i in range(1,len(values)):
                student = values[i]

                if len(student) <2: continue

                first_name = " ".join(student[1].split())
                last_name = " ".join(student[2].split())

                login_day = student[0].split('/')[1]
                now_day = datetime.now().day

                if(int(login_day) != int(now_day)):
                    self.old_attendance.append(i)
                    continue
                
                found = False
                for student in self.students_attendance:
                    if student['first_name'] == first_name and student['last_name'] == last_name:
                        if student['attendance'] == "ABSENT": student['attendance'] = "LATE"
                        else: student['attendance'] = "PRESENT"
                        
                        found = True
                        break  
                if not found:
                    student = {
                        'first_name' : first_name,
                        'last_name' : last_name,
                        'attendance' : "WRONG",
                        "period" : period,
                        "day" : day
                    }
                    self.students_attendance.append(student)
            if len(self.old_attendance)>0: self.deleteRows(sheet_id, self.old_attendance[0], self.old_attendance[-1])

        except HttpError as err:
            print(err)

    def getAbsentStudents(self):
        for student in self.students_attendance:
            for line in self.absent_students:
                if(student['first_name'] in line and student['last_name'] in line):
                    student['attendance'] = "ABSENT"
                    break



    def add_active_sheets(self):
        SPREADSHEET_ID = self.config.getSpreadSheetID()
        if(SPREADSHEET_ID == "000000000"):return
        service = build('sheets', 'v4', credentials=self.creds)
        sheet = service.spreadsheets()
        
        sheets = sheet.get(spreadsheetId = SPREADSHEET_ID).execute()

        for active_sheets in sheets['sheets']:
            self.sheets_list.append(
                {
                    "title" : active_sheets['properties']['title'],
                    "ID" : active_sheets['properties']['sheetId']
                }
            )

    def deleteRows(self, sheet_id, start_row, end_row):
        service = build('sheets', 'v4', credentials=self.creds)
        request_body = {
            "requests": 
                {
                    "deleteDimension": {
                        "range": {
                        "sheetId": sheet_id,
                        "dimension": "ROWS",
                        "startIndex": start_row,
                        "endIndex": end_row+1
                        }
                    }
                }
        }
        service.spreadsheets().batchUpdate(
            spreadsheetId=self.config.getSpreadSheetID(),
            body=request_body
        ).execute()


    def getAbsentFile(self):
        if os.path.exists("apis\\temp.txt"):
            os.remove("apis\\temp.txt")
        file = open("absent.txt", "r")
        hasContent = False
        for line in file:
            if not hasContent: hasContent = True
            self.absent_students.append(line)
        file.close()
        return hasContent

    def setAbsentFile(self, file_location):
        if(file_location == ""): return
       
        try:
            pytesseract.pytesseract.tesseract_cmd = r'apis\\Tesseract-OCR\\tesseract.exe'
            pages = convert_from_path(file_location, 500,poppler_path=r'apis\\Poppler\\bin')
        except:
            print("Could not find API's. Make sure they are in the apis folder.")
            return False
        file = open("absent.txt", "w")

        add_lines = []
        for imgBlob in pages:
            text = pytesseract.image_to_string(imgBlob)
            
            for line in text.split("\n"):
                if "," in line:
                    sorted_line = line.replace("|","").replace("=","").replace("  ", " ")
                    newstring = ''.join([i for i in sorted_line if not i.isdigit()])
                    add_lines.append(newstring.strip() + "\n")
        file.writelines(add_lines)
        file.close()     
        os.startfile(file_location)   
        return True
                    

    def readStudentList(self, sheet):
        try:
            service = build('sheets', 'v4', credentials=self.creds)
            SAMPLE_RANGE_NAME = sheet + "!A:C"
            SPREADSHEET_ID = "16iAuYMIQOfqgzgiNXYY3Unyyqpyh4eSb-wivL2_LkB8"
            
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()

            values = result.get('values', [])

            file = open("students.txt", "a")
            for i in range(1,len(values)):
                student = values[i]

                last_name = student[0].split(',')[0].strip()
                first_name = student[0].split(',')[1].strip()
                
                period_col = student[2].split('(')[0]
                period = period_col if not "-" in period_col else period_col[0] + period_col[1] + period_col[2]
                day = student[2].split('(')[1].strip().replace('-', "")
                file.write(first_name + ", " + last_name + " : " + period + " : " + day[:-1] + "\n")
            file.close()
        except HttpError as err:
            print(err)

    def setKeyFile(self):
        try:
            self.creds = service_account.Credentials.from_service_account_file(
                self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
            return True
        except:
            return False




