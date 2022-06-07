import sys, json, csv
from datetime import datetime
import utility.timestamp_utility as stamp
import sheets.LO_OverDaysPersistent as s3

class SecondSheet:

    outputFilename: str = None
    students_data: list = None

    def __init__(self, filename, students_data):
        self.outputFilename = filename
        self.students_data = students_data

    def run(self):
        data = self.generateData()
        if self.generateTSVFile(data):
            sys.stdout.write("\nAll done, data stored in " + self.outputFilename + "\n")
        else:
            sys.stdout.write("\nError\n")

    def generateData(self) -> str:
        data = {}
        allLOs = s3.readLearningObjectiveCSV(self)
        
        for learningObjectives in self.students_data:
            
            # getting data from each learning objectives
            ID = learningObjectives["ID"]
            strand = learningObjectives["strand"]
            short_goal = learningObjectives["goal_Short"]
            goal = next(LO for LO in allLOs if LO['ID'] == ID)['goal']
            objectives = next(LO for LO in allLOs if LO['ID'] == ID)['objectives']
            core = learningObjectives["isCore"]
            evalScore = learningObjectives["eval_score"]
            evalDate = learningObjectives["eval_date"]

            # creating empty data if nil
            if ID not in data: 
                data[ID] = {}
                data[ID]["strand"] = strand
                data[ID]["goal"] = goal
                data[ID]["short_goal"] = short_goal
                data[ID]["objectives"] = objectives
                data[ID]["core"] = core
                data[ID]["level1"] = {}
                data[ID]["level2"] = {}
                data[ID]["level3"] = {}
                data[ID]["level4"] = {}
                data[ID]["level5"] = {}
            
            # filling data
            lastScore = 0
            lastDate = 0
            for i in range(len(evalScore)):

                # getting score and date
                evalScoreValue = evalScore[i]
                evalDateValue = evalDate[i]

                # 0 score are not counted
                if evalScoreValue == 0: continue

                # transforming data to string
                evalScoreFullString = "level" + str(evalScoreValue)
                lastScoreFullString = "level" + str(lastScore)
                evalDateTimestamp = stamp.adjust(evalDateValue)
                lastDateTimestamp = stamp.adjust(lastDate)
                
                # subtracting if the score has enhanced
                if lastScore != 0:
                    data[ID][lastScoreFullString][lastDateTimestamp] -= 1
                
                if evalDateTimestamp not in data[ID][evalScoreFullString]: 
                    data[ID][evalScoreFullString][evalDateTimestamp] = 0
                data[ID][evalScoreFullString][evalDateTimestamp] += 1

                lastScore = evalScoreValue
                lastDate = evalDateValue

                for j in range(1,6):
                    if j != evalScoreValue:
                        a = "level" + str(j)
                        if evalDateTimestamp not in data[ID][a]:
                            data[ID][a][evalDateTimestamp] = 0
         
        for LO in allLOs:
            if LO['ID'] not in data.keys():
                data[LO['ID']] = {}
                data[LO['ID']]["strand"] = LO['strand']
                data[LO['ID']]["goal"] = LO['goal']
                data[LO['ID']]["short_goal"] = LO['short']
                data[LO['ID']]["objectives"] = LO['objectives']
                data[LO['ID']]["core"] = "CORE" if LO['core'] else "ELECTIVE"

                data[LO['ID']]["level1"] = {}
                data[LO['ID']]["level2"] = {}
                data[LO['ID']]["level3"] = {}
                data[LO['ID']]["level4"] = {}
                data[LO['ID']]["level5"] = {}

            data[LO['ID']]["backend"] = LO['backend']
            data[LO['ID']]["business"] = LO['business']
            data[LO['ID']]["design"] = LO['design']
            data[LO['ID']]["frontend"] = LO['frontend']
            data[LO['ID']]["gameDesign"] = LO['gameDesign']
            data[LO['ID']]["gameDeveloper"] = LO['gameDeveloper']
            data[LO['ID']]["projectManagement"] = LO['projectManagement']

        data_string = json.dumps(self.addEmptyDate(data))
        # with open("output/test.json", 'w') as f:
        #     f.write(data_string)
        #     f.close()

        return data_string

    def addEmptyDate(self, data) -> str:

        # function to fill the timestamp with empty data
        def fillEmptyData(data, timestamp):
            for ID in data:
                for i in range(1, 6):
                    value = stamp.adjust(timestamp)
                    if value not in data[ID]["level" + str(i)]:
                        data[ID]["level" + str(i)][value] = 0
            return data

        # calculate dates extremes
        minTimestamp = float("inf")
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        maxTimestamp = float(timestamp)
        for ID in data:
            for date in data[ID]["level1"].keys():
                if float(date) < minTimestamp:
                    minTimestamp = float(date)

        # saving 0 for each timestamp
        timestamp = minTimestamp
        while timestamp < maxTimestamp:
            data = fillEmptyData(data, timestamp)
            
            # adding one day to the timestamp
            timestamp += 24*60*60

        data = fillEmptyData(data, maxTimestamp)

        return data

    def generateTSVFile(self, jsonData: str) -> bool:
        try:

            # returns JSON object as a dictionary
            data = json.loads(jsonData)

            # defining support arrays
            allRows = []
            experienceLevels = ["No Exposure","Beginning","Progressing","Proficient","Exemplary"]

            # the first row is a litte bit particular
            #backend;business;design;frontend;gameDesign;gameDeveloper;projectManagement
            firstRow = ["ID","Strand","goal","Short Goal","objectives","Core","Level","backend","business","design","frontend","gameDesign","gameDeveloper","projectManagement"]
            level_Datas = [*data[list(data.keys())[0]]["level1"]]
            level_Datas.sort()
            for level_Data in level_Datas:
                date_time = datetime.fromtimestamp(int(level_Data)).strftime('%Y-%b-%d').upper()
                firstRow.append(date_time)

            # appending the first row
            allRows.append(firstRow)
            #["ID","Strand","goal","Short Goal","objectives","Core","Level"]
            # for each learning objective that we have in the json
            for key in data.keys():
                # fo this operation 5 time, each for an evaluation level
                for i in range(1,6):
                    # prepare the array
                    row = []
                    # insert the ID
                    row.append(key)
                    # input the strand
                    row.append(data[key]["strand"])
                    # input the goal
                    row.append(data[key]["goal"])
                    # insert the goal
                    row.append(data[key]["short_goal"])
                    # input the goal
                    row.append(data[key]["objectives"])
                    #insert the core
                    row.append(data[key]["core"])
                    # insert the level of expertice
                    row.append(key + " - " + experienceLevels[i-1])
                    rubrics = ["backend","business","design","frontend","gameDesign","gameDeveloper","projectManagement"]

                    for rubric in rubrics:
                        present = 0
                        if data[key][rubric] in experienceLevels:
                            present = experienceLevels.index(data[key][rubric])
                            row.append("1" if present == (i-1) else "0")
                        else:
                            row.append("0")


                    # insert the rubric level expected for Backend path
                    rubricAssociated = "0"
                    if data[key]["backend"] in experienceLevels:
                        backendPath = experienceLevels.index(data[key]["backend"])
                    row.append("1" if data[key]["backend"]!= "" else "0")
                    # insert the rubric level expected for Business path
                    row.append("1" if data[key]["business"]!= "" else "0")
                    # insert the rubric level expected for Design path
                    row.append("1" if data[key]["design"]!= "" else "0")
                    # insert the rubric level expected for Frontend path
                    row.append("1" if data[key]["frontend"]!= "" else "0")
                    # insert the rubric level expected for Game Design path
                    row.append("1" if data[key]["gameDesign"]!= "" else "0")
                    # insert the rubric level expected for Game Developer path
                    row.append("1" if data[key]["gameDeveloper"]!= "" else "0")
                    # insert the rubric level expected for Project Management path
                    row.append("1" if data[key]["projectManagement"]!= "" else "0")

                    # check how many student are present for that day
                    level_Datas = [*data[key]["level"+str(i)]]
                    level_Datas.sort()
                    for lvl in level_Datas:
                        row.append(data[key]["level"+str(i)][lvl])
                    
                    # add row to the array
                    allRows.append(row)

            # write on the file
            with open(self.outputFilename, 'w') as out_file:
                tsv_writer = csv.writer(out_file, delimiter='\t')
                for singleRow in allRows:
                    tsv_writer.writerow(singleRow)
            
                out_file.close()
            print("@@@@@@@")
            return True

        except Exception as e: 
            sys.stdout.write("\n" + str(e) + "\n")
            return False
