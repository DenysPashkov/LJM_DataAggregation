import sys, json, csv
from datetime import datetime
import utility.dropbox_manager as dropbox
import sheets.LO_OverChallengesWeeks as s1
import sheets.LO_OverDaysNotPersistent as s2
import sheets.LO_OverDaysPersistent as s3
import sheets.StudentEvaluations_OverDaysNotPersistent as s4




if __name__ == "__main__":

    sys.stdout.write("Getting data...\n")
    students_data, filteredStudents = dropbox.getStudentsContent()

    OUTPUT_PATH = 'output/'
    SHEET1_OUTPUT_FILE = 'LO_OverChallengesWeeks_' + datetime.now().strftime("%Y|%m|%d_%H:%M_") + f"{len(filteredStudents)}" + '.tsv'
    SHEET2_OUTPUT_FILE = 'LO_OverDaysNotPersistent_' + datetime.now().strftime("%Y|%m|%d_%H:%M_") + f"{len(filteredStudents)}" + '.tsv'
    SHEET3_OUTPUT_FILE = 'LO_OverDaysPersistent_' + datetime.now().strftime("%Y|%m|%d_%H:%M_") + f"{len(filteredStudents)}" + '.tsv'
    SHEET4_OUTPUT_FILE = 'StudentEvaluations_OverDaysNotPersistent_' + datetime.now().strftime("%Y|%m|%d_%H:%M_") + f"{len(filteredStudents)}" + '.tsv'
    
    #sys.stdout.write("\nGenerating first sheet...")
    #first_sheet = s1.FirstSheet(OUTPUT_PATH + SHEET1_OUTPUT_FILE, students_data.copy())
    #first_sheet.run()

    sys.stdout.write("\nGenerating second sheet...")
    second_sheet = s2.SecondSheet(OUTPUT_PATH + SHEET2_OUTPUT_FILE, students_data.copy())
    second_sheet.run()

    sys.stdout.write("\nGenerating forth sheet...")
    third_sheet = s3.ThirdSheet(OUTPUT_PATH + SHEET3_OUTPUT_FILE, filteredStudents.copy())
    third_sheet.run()

    sys.stdout.write("\nGenerating forth sheet...")
    forth_sheet = s4.ForthSheet(OUTPUT_PATH + SHEET4_OUTPUT_FILE, filteredStudents.copy())
    forth_sheet.run()


    