import configparser
import os
import urllib3
import requests
from datetime import date

config = configparser.ConfigParser()

class Files: 
    def __init__(self):
        config.read("config.ini")
        self.checkFiles()
        self.checkSections()
    
    def checkFiles(self):
        if not os.path.exists("config.ini"): 
            open("config.ini", "x")
        if not os.path.exists("students.txt"): 
            open("students.txt", "x")
        if not os.path.exists("absent.txt"): 
            open("absent.txt", "x")
        if not os.path.exists("students.txt"): 
            open("students.txt", "x")
        if not os.path.exists("version.txt"): 
            file = open("version.txt", "x")
            file.write("1.0")
            file.close()

    def checkSections(self):
        if not config.has_section("Sheet_Info"):
            config.add_section("Sheet_Info")
        if config.has_section("Periods_Settings") == False:
            config.add_section("Periods_Settings")
        if not config.has_section("Time"):
            config.add_section('Time')
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def writeSpreadSheetLink(self, link : str):
        link_ID = link.split('/')[5]
        config.set("Sheet_Info","link", link)
        config.set("Sheet_Info","id", link_ID)
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def getPeriodList(self):
        default_period_list = ["Period 1", "Period 2", "Period 3"]
        if not config.has_option("Periods_Settings", "period_list"): 
            config.set("Periods_Settings", "period_list", str(default_period_list))
            with open("config.ini", "w") as configfile:
                config.write(configfile)

        return config.get("Periods_Settings", "period_list")

    def writePeriodList(self, periods):
        config.set("Periods_Settings","period_list", str(periods))
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def getSpreadSheetLink(self):
        if(config.has_option("Sheet_Info", "link")): return config.get("Sheet_Info", "link")
        else: return "Please Enter the URL of a Google Sheet"

    def getSpreadSheetID(self):
        if(config.has_option("Sheet_Info", "id")): return config.get("Sheet_Info", "id")
        else: return "Please Enter the URL of a Google Sheet"

    def createOption(self, section, option, default):
        if config.has_section(section) == False:
            config.add_section(section)

        config.set(section, option, default)

    def getPeriodSheetName(self, period):
        if not config.has_option("Periods_Settings", "period." + period + ".sheet.name"):  
            return "Select A Form!"
        return config.get("Periods_Settings", "period." + period + ".sheet.name")     

    def getPeriodSheetID(self, period):
        if not config.has_option("Periods_Settings", "period." + period + ".sheet.id"):  
            return "000000000"
        return config.get("Periods_Settings", "period." + period + ".sheet.id")

    def setPeriodSheetName(self, period, name):
        config.set("Periods_Settings", "period." + period + ".sheet.name", str(name))
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def setPeriodSheetID(self, period, id):
        config.set("Periods_Settings", "period." + period + ".sheet.id", str(id))
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def checkPeriodConfigInfo(self, period):
        if not config.has_option("Periods_Settings", "period." + period[-1] + ".sheet.name"):
            config.set("Periods_Settings", "period." + period[-1] + ".sheet.name", "Select A Form!")
        if not config.has_option("Periods_Settings", "period." + period[-1] + ".sheet.id"):
            config.set("Periods_Settings", "period." + period[-1] + ".sheet.id", "0000000000")

        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def setLastRanTime(self):      
        today = date.today()
        config.set("Time", "last_ran_day", str(today.strftime("%d")))
        with open("config.ini", "w") as configfile:
                config.write(configfile)
        
    def getLastRanTime(self):
        if not config.has_option("Time", "last_ran_day"):
            today = date.today()
            return today.strftime("%d")
        return config.get("Time", "last_ran_day")
    
    def clearAbsentFile(self):
        open("absent.txt", "w").close()
    
    def updateAviable(self):
        http = urllib3.PoolManager()
        user_version_file = open("version.txt", "r")
        user_version = user_version_file.readline()
        web_version = http.request('GET', 'https://benevolent-swan-bb1bee.netlify.app/version.txt')

        if(float(user_version) != float(web_version.data)):
            return True
        return False

    def writeVersion(self, version):
        with open('version.txt', 'w') as f:
            f.write(str(version))
    
    def getWebVersion(self):
        http = urllib3.PoolManager()
        web_version = http.request('GET', 'https://benevolent-swan-bb1bee.netlify.app/version.txt')
        return float(web_version.data)

    def getUserVersion(self):
        user_version_file = open("version.txt", "r")
        user_version = user_version_file.readline()
        return user_version

    def downloadNewVersion(self):
        
        downloadURL = "https://github.com/Tiskua/Attendance/raw/main/GUI.exe"
        try:
            req = requests.get(downloadURL)
            with open("GUI-" + str(self.getWebVersion()) + ".exe", 'xb') as f:
                for chunk in req.iter_content(chunk_size=8192):
                    if chunk: f.write(chunk)
            return True
        except:
            print("There was an error trying to download from the URL!")
            return False

        

