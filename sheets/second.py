import sys, json, csv
from datetime import datetime
import utility.timestamp_utility as stamp

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
        for learningObjectives in self.students_data:
            
            # getting data from each learning objectives
            ID = learningObjectives["ID"]
            strand = learningObjectives["strand"]
            short_goal = learningObjectives["goal_Short"]
            core = learningObjectives["isCore"]
            evalScore = learningObjectives["eval_score"]
            evalDate = learningObjectives["eval_date"]

            # creating empty data if nil
            if ID not in data: 
                data[ID] = {}
                data[ID]["strand"] = strand
                data[ID]["short_goal"] = short_goal
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
        maxTimestamp = float("-inf")
        for ID in data:
            for date in data[ID]["level1"].keys():
                if float(date) < minTimestamp:
                    minTimestamp = float(date)
                elif float(date) > maxTimestamp:
                    maxTimestamp = float(date)

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
            firstRow = ["ID","Strand","Short Goal","Core", "Level"]
            level_Datas = [*data[list(data.keys())[0]]["level1"]]
            level_Datas.sort()
            for level_Data in level_Datas:
                date_time = datetime.fromtimestamp(int(level_Data)).strftime("%Y-%m-%d")
                firstRow.append(date_time)

            # appending the first row
            allRows.append(firstRow)

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
                    # insert the goal
                    row.append(data[key]["short_goal"])
                    #insert the core
                    row.append(data[key]["core"])
                    # insert the level of expertice
                    row.append(key + " - " + experienceLevels[i-1])

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

            return True

        except Exception as e: 
            sys.stdout.write("\n" + str(e) + "\n")
            return False
