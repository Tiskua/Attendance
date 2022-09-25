import configparser
from datetime import date

config = configparser.ConfigParser()

class Files: 
    def __init__(self):
        config.read("config.ini")

    def writeSpreadSheetLink(self, link : str):
        
        if config.has_section("Sheet_Info") == False:
            config.add_section("Sheet_Info")

        link_ID = link.split('/')[5]
        config.set("Sheet_Info","link", link)
        config.set("Sheet_Info","id", link_ID)
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def getPeriodList(self):
        default_period_list = ["Period 1", "Period 2", "Period 3"]
        if config.has_section("Periods_Settings") == False:
            config.add_section("Periods_Settings")
            config.set("Periods_Settings", "period_list", str(default_period_list))
            with open("config.ini", "w") as configfile:
                config.write(configfile)
        elif config.has_option("Periods_Settings", "period_list") == False: 
            config.set("Periods_Settings", "period_list", str(default_period_list))
            with open("config.ini", "w") as configfile:
                config.write(configfile)

        return config.get("Periods_Settings", "period_list")

    def writePeriodList(self, periods):
        config.set("Periods_Settings","period_list", str(periods))
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    def getSpreadSheetLink(self):
        # config.read("config.ini")
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
        if not config.has_section("Time"):
            config.add_section('Time')
            
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
    