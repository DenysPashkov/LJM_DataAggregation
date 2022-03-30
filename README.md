This script can be used to manage students data.
Full documentation on Notion.

## Introduction

First of all it will connect to Dropbox to download the students data (using API).
Then from students data (in json format) it will create a unique json 
file that store all the user learning objectives archived.
At the end, this json file is going to be converted into a .tsv file 
in order to be able to import it in Numbers.

## Notes

If you want to change the filename of the ouput .tsv file, change the global 
variable SHEET1_OUTPUT_FILE and SHEET2_OUTPUT_FILE in run.py to wathever you want; 
right now the name convention used is LJM_Data_X_sheet_YYYYMMDD_HHmmss.tsv
The output files will be stored into /output folder.

In order to allow connection with Dropbox a token is required; you can set 
it in utility/dropbox_manager.py changing the global variable TOKEN.
# LJM_Backend
