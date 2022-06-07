import sys, json, csv
import requests, json
from datetime import datetime

TOKEN = 'keyN55muBclzvZXAb'

def _getData(offset : str):

    url = "https://api.airtable.com/v0/app26CHrOG4n8za36/LJM"

    headers = {
        'Authorization': 'Bearer ' + TOKEN,
        'Content-Type': 'application/json'
    }

    params = {}

    if offset != "" :
        params = {'offset': offset}

    response = requests.request("GET", url,params=params, headers=headers)

    return response.json()

def _deleteReplicatedStudents(students: []):
    addedStudents = []
    for index in range(len(students)):
        tempDictionary = {}
        tempDictionary["index"] = students[index]
        tempDictionary["createdTime"] = students[index]["date"]
        tempDictionary["studentID"] = students[index]["fields"]["ID"]
        addedStudents.append(tempDictionary)

    tempArray = addedStudents.copy()
    indexOfBiggest = {}
    dateOfBiggest = {}
    for student in addedStudents:
        for student2 in addedStudents:
            if student["studentID"] == student2["studentID"]:
                if student["studentID"] in indexOfBiggest.keys():
                    if student2["createdTime"] > dateOfBiggest[student2["studentID"]]:
                        indexOfBiggest[student2["studentID"]] = student2["index"]
                        dateOfBiggest[student["studentID"]] = student2["createdTime"]
                elif student["createdTime"] < student2["createdTime"]:
                    indexOfBiggest[student["studentID"]] = student2["index"]
                    dateOfBiggest[student["studentID"]] = student2["createdTime"]
                else:
                    indexOfBiggest[student["studentID"]] = student["index"]
                    dateOfBiggest[student["studentID"]] = student["createdTime"]

    returnArray = []
    for key in indexOfBiggest.keys():
        returnArray.append(indexOfBiggest[key])

    return returnArray
    

def getStudentsContent():
    dataArray = []
    allStudents = []
    rawDataArray = []

    studentsData = _getData("")

    allStudents += studentsData["records"]

    while "offset" in studentsData.keys():
        studentsData = _getData(studentsData["offset"])
        allStudents += studentsData["records"]

    for student in allStudents:
        strtime = student["createdTime"][:-5].replace("T", " ")
        date_time_obj = datetime.strptime(strtime, '%Y-%m-%d %H:%M:%S')
        student["date"] = date_time_obj
            
    filteredStudents = _deleteReplicatedStudents(allStudents)

    for student in filteredStudents:
        rawDataArray.append(student["fields"]["data"])

    for rawData in rawDataArray:
        peppe = rawData
        json_object = json.loads(peppe)
        dataArray+=json_object
        
    #sys.stdout.write(f"@@@@@@ {dataArray[0]['fields']['data']}" )
    #sys.stdout.write(f"@@@@@@ {filteredStudents[0]['fields']}" )

    return dataArray, filteredStudents;

getStudentsContent()