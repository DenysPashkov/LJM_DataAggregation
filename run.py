import sys, json, csv
from datetime import datetime
import utility.dropbox_manager as dropbox
import sheets.first as s1
import sheets.second as s2

OUTPUT_PATH = 'output/'
SHEET1_OUTPUT_FILE = 'LJM_Data_first_sheet_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.tsv'
SHEET2_OUTPUT_FILE = 'LJM_Data_second_sheet_' + datetime.now().strftime("%Y%m%d_%H%M%S") + '.tsv'

if __name__ == "__main__":

    sys.stdout.write("Getting data...\n")
    students_data = dropbox.getStudentsContent()
    
    sys.stdout.write("\nGenerating first sheet...")
    first_sheet = s1.FirstSheet(OUTPUT_PATH + SHEET1_OUTPUT_FILE, students_data.copy())
    first_sheet.run()

    sys.stdout.write("\nGenerating second sheet...")
    second_sheet = s2.SecondSheet(OUTPUT_PATH + SHEET2_OUTPUT_FILE, students_data.copy())
    second_sheet.run()
    