import os
import requests, json
import numpy as np
import pymysql
from math import radians, sin, cos, sqrt, atan2
from typing import Union
from fastapi import FastAPI, Query, HTTPException
from pymongo import MongoClient


app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath("./")))
secret_file = os.path.join(BASE_DIR, 'secret.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        errorMsg = "Set the {} environment variable.".format(setting)
        return errorMsg

## DB connect
HOSTNAME = get_secret("Local_Mongo_Hostname")
USERNAME = get_secret("Local_Mongo_Username")
PASSWORD = get_secret("Local_Mongo_Password")

client = MongoClient(f'mongodb://{USERNAME}:{PASSWORD}@{HOSTNAME}')
db = client['bikeproject']
temp = db["temp"]
subwaypath = db["subwaypath"]
buspath = db["buspath"]
bikepath = db["bikepath"]

DBHOSTNAME = get_secret("Mysql_Hostname")
DBPORT = int(get_secret("Mysql_Port"))
DBUSERNAME = get_secret("Mysql_Username")
DBPASSWORD = get_secret("Mysql_Password")
DB = get_secret("Mysql_DBname")

connection = pymysql.connect(host=DBHOSTNAME, port=DBPORT, user=DBUSERNAME, password=DBPASSWORD, database=DB)

## function
def haversine_distance(x1, y1, x2, y2):
    R = 6371.0

    y1 = radians(y1)
    x1 = radians(x1)
    y2 = radians(y2)
    x2 = radians(x2)

    dy = y2 - y1
    dx = x2 - x1

    a = sin(dy / 2)**2 + cos(y1) * cos(y2) * sin(dx / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c * 1000  

    return distance

## API
@app.get("/")
def read_root():
    print("connected...")
    return {"Hi": "World"}

## search + temp 저장
tempLastId = temp.count_documents({}) + 1
subwayPathId = subwaypath.count_documents({}) + 1
busPathId = buspath.count_documents({}) + 1

@app.get("/searchSubway")
async def searchSubwayPath(Sx: float = Query(..., description="출발지 x 좌표"),
                     Sy: float = Query(..., description="출발지 y 좌표"),
                     Ex: float = Query(..., description="도착지 x 좌표"),
                     Ey: float = Query(..., description="도착지 y 좌표")):
    Odsay_apiKey = get_secret("Odsay_apiKey")
    global tempLastId
    url = 'https://api.odsay.com/v1/api/searchPubTransPathT?'
    params = f"SX={Sx}&SY={Sy}&EX={Ex}&EY={Ey}&apiKey={Odsay_apiKey}&SearchPathType=1"
    url += params

    data = requests.get(url).json()
    data["TempId"] = f"{tempLastId:04d}"
    tempLastId += 1
    temp.insert_one(data)
    return {201: "Created", "coordinates":[Sx, Sy, Ex, Ey], "TempId": data["TempId"]}

@app.get("/searchBus")
async def searchBusPath(Sx: float = Query(..., description="출발지 x 좌표"),
                     Sy: float = Query(..., description="출발지 y 좌표"),
                     Ex: float = Query(..., description="도착지 x 좌표"),
                     Ey: float = Query(..., description="도착지 y 좌표")):
    Odsay_apiKey = get_secret("Odsay_apiKey")
    global tempLastId
    url = 'https://api.odsay.com/v1/api/searchPubTransPathT?'
    params = f"SX={Sx}&SY={Sy}&EX={Ex}&EY={Ey}&apiKey={Odsay_apiKey}&SearchPathType=2"
    url += params

    data = requests.get(url).json()
    data["TempId"] = f"{tempLastId:04d}"
    tempLastId += 1
    
    temp.insert_one(data)
    return {201: "Created", "coordinates":[Sx, Sy, Ex, Ey], "TempId": data["TempId"]}


## 정제 path data 저장

@app.post("/saveSubwayPath")
async def saveSubwayPath(data: dict):  #{"coordinates":[127.027619, 37.497952, 126.993598, 37.487707], "TempId": "0016"}
    global subwayPathId
    coordinates = data["coordinates"]
    cleanData = temp.find_one({"TempId": data["TempId"]}, {"_id":0})

    if not cleanData:
        raise HTTPException(status_code=404, detail="Data not found")

    #mongo.subwaypath 에 저장
    cleanData = cleanData["result"]["path"][0]
    #print(cleanData)
    cleanData["coordinates"] = coordinates
    cleanData["SId"] = f"{subwayPathId:04d}"
    subwaypath.insert_one(cleanData)
    #result = subwaypath.find_one({"SId":cleanData["SId"]}, {"_id":0})

    subwayPathId += 1  
    return {201: "Created", "SId":cleanData["SId"]}


## 버스 경로 
@app.post("/saveBusPath")
async def saveBusPath(data: dict):
    global busPathId
    coordinates = data["coordinates"]
    Sx = coordinates[0]
    Sy = coordinates[1]
    cleanData = temp.find_one({"TempId": data["TempId"]}, {"_id":0})

    if not cleanData:
        raise HTTPException(status_code=404, detail="Data not found")

    cleanData = cleanData["result"]["path"][0]  #추출
    cleanData["coordinates"] = coordinates
    cleanData["BId"] = f"{busPathId:04d}"
    buspath.insert_one(cleanData)
    #result1 = buspath.find_one({"BId":cleanData["BId"]}, {"_id":0})

    Ex = coordinates[2]
    Ey = coordinates[3]
    Lx = cleanData["subPath"][len(cleanData["subPath"])-2]["endX"]
    Ly = cleanData["subPath"][len(cleanData["subPath"])-2]["endY"]
    print(Ex, Ey, Lx, Ly)
    searchCor = {"station": {"Ex":Ex, "Ey":Ey, "Lx":Lx, "Ly":Ly}}
    searchCor["BId"] = f"{busPathId:04d}"
    print(searchCor)
    bikepath.insert_one(searchCor)
    #result2 = bikepath.find_one({"BId":cleanData["BId"]}, {"_id":0})
    
    busPathId += 1  
    return {201: "Created", "BId":cleanData["BId"]}
    

# 따릉이 경로 검증
@app.patch("/bikeStation")
def find_bike_station(data: dict): #   {"BId": "0014"}
    bikeStation =requests.get('http://192.168.1.64:5000/bikeStation').json()
    cor = bikepath.find_one(data, {"_id":0})
    Ex = cor["station"]["Ex"]
    Ey = cor["station"]["Ey"]
    Lx = cor["station"]["Lx"]
    Ly = cor["station"]["Ly"]

    closeBikeStationL = []
    closeBikeStationE = []

    for i in bikeStation:
        distL = round(haversine_distance(Lx, Ly, i["x"], i["y"]))
        distE = round(haversine_distance(Ex, Ey, i["x"], i["y"]))
        if  distL <= 500:
            closeBikeStationL.append({"station": {"Lx":Lx, "Ly":Ly, "Bx":i["x"], "By":i["y"]}, "dist":distL, "bikeStaionNo":i["stationNo"], "bikeStationName":i["stationName"]})
        if distE <= 500:
            closeBikeStationE.append({"station": {"Ex":Ex, "Ey":Ey, "Bx":i["x"], "By":i["y"]}, "dist":distE, "bikeStaionNo":i["stationNo"], "bikeStationName":i["stationName"]})

    closeBikeStationL.sort(key=lambda x: x['dist'])
    closeBikeStationE.sort(key=lambda x: x['dist'])
    print (closeBikeStationL)
    print (closeBikeStationE)

    if (len(closeBikeStationL) >=1) and (len(closeBikeStationE) >=1):
        searchStationReult = {"lastBikeStaiton":closeBikeStationL[0], "endBikeStaiton":closeBikeStationE[0]}
    else: 
        searchStationReult = {"bikeStation":None}

    print(searchStationReult)

    # 계산
    lastBikeStaiton = searchStationReult["lastBikeStaiton"]
    endBikeStaiton = searchStationReult["endBikeStaiton"]
    path =[]
    #to BikeStation
    walktoBikeDist = lastBikeStaiton["dist"]
    walktoBikeTime = (walktoBikeDist/5000)*60   #m/min
    if walktoBikeTime <1:
        walktoBikeTime = 1
    walktoBike = {"trafficType": 3,
                "distance": walktoBikeDist,
                "sectionTime": walktoBikeTime,
                "startX":Lx,
                "startY":Ly,
                }
    path.append(walktoBike)

    #따릉 경로 만들기
    walktoBikeDist = round(haversine_distance(lastBikeStaiton["station"]["Bx"],lastBikeStaiton["station"]["By"], endBikeStaiton["station"]["Bx"], endBikeStaiton["station"]["By"]))
    walktoBikeTime = (walktoBikeDist/5000)*60   #m/min
    walktoBike = {"trafficType": 4,
                "distance": walktoBikeDist,
                "sectionTime": walktoBikeTime,
                "startX":lastBikeStaiton["station"]["Bx"],
                "startY":lastBikeStaiton["station"]["By"],
                "endX":endBikeStaiton["station"]["Bx"],
                "endY":endBikeStaiton["station"]["By"]}
    path.append(walktoBike)

    # from BikeStation
    walkfromBikeDist = endBikeStaiton["dist"]
    walkfromBikeTime = round((walkfromBikeDist/12000)*60)   #m/min
    if walkfromBikeTime <1:
        walkfromBikeTime = 1
    walkfromBike = {"trafficType": 3,
                "distance": walkfromBikeDist,
                "sectionTime": walkfromBikeTime
                }
    path.append(walkfromBike)

    filter = data
    updateData = {
        "$set": {
        "station": searchStationReult,  
        "subPath": path
        }
    }
    bikepath.update_one(filter, updateData)
    updatepath = bikepath.find_one(data, {"_id":0})
    return {203: "Updated", "BId": updatepath["BId"]}


# 버스 수정 경로 만들기
@app.patch("/updateBusPath")
async def updateBusPath(data: dict):  # {"BId": "0014"}
    global busPathId
    busPath = buspath.find_one(data, {"_id":0})
    bikePath = bikepath.find_one(data, {"_id":0})

    if not busPath or not bikePath:
        raise HTTPException(status_code=404, detail="Bus or bike path not found")

    busBikepath = busPath["subPath"]
    subPathNo = len(busBikepath)
    walkDist = busBikepath[subPathNo-1]["distance"]
    walkTime = busBikepath[subPathNo-1]["sectionTime"]
    
    newDist = busPath["info"]["trafficDistance"]
    newWalk = busPath["info"]["totalWalk"] - walkTime
    newTime = busPath["info"]["totalTime"] - walkTime

    del busBikepath[subPathNo-1]
    for i in bikePath["subPath"]:
        if i["trafficType"] == 3:
            newWalk += i["distance"]
        else:
            newDist += i["distance"]
        newTime += i["sectionTime"]
        busBikepath.append(i)

    filter = data
    updateData = {
        "$set": {
        "subPath": busBikepath,  
        "info.trafficDistance": newDist,
        "info.totalWalk": newWalk,
        "info.totalTime": newTime
        }
    }

    buspath.update_one(filter, updateData)
    #result = buspath.find_one(data, {"_id":0})

    return {203: "Updated", "BId":data["BId"]}


#결과 비교하여 인덱스 저장하기
@app.post("/saveSql")
async def saveSql(data: dict): #{"SId": "0014", "BId": "0014"}
    if data["SId"]==data["BId"]:
        SearchId = data["SId"]
    else:
        raise HTTPException(status_code=406, detail="Data error")

    subway = subwaypath.find_one({"SId":data["SId"]}, {"_id":0})
    STotalTime = round(subway["info"]["totalTime"])
    STotalDistance = round(subway["info"]["trafficDistance"])
    busbike = buspath.find_one({"BId":data["BId"]}, {"_id":0})
    BTotalTime = round(busbike["info"]["totalTime"])
    BTotalDistance = round(busbike["info"]["trafficDistance"])
    Optipath = "지하철" if STotalTime < BTotalTime else "버스와자전거"
    Diff = BTotalTime - STotalTime if STotalTime < BTotalTime else STotalTime - BTotalTime
    
    Sx = subway["coordinates"][0]
    Sy = subway["coordinates"][1]
    Ex = subway["coordinates"][2]
    Ey = subway["coordinates"][3]
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    print(SearchId, Sx, Sy, Ex, Ey, STotalTime, STotalDistance, BTotalTime, BTotalDistance, Optipath, Diff)
    sql = "INSERT INTO bikesql.`sidx` (SearchId, Sx, Sy, Ex, Ey, STotalTime, STotalDistance, BTotalTime, BTotalDistance, Optipath, Diff) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (SearchId, Sx, Sy, Ex, Ey, STotalTime, STotalDistance, BTotalTime, BTotalDistance, Optipath, Diff)
    cursor.execute(sql, values)
    connection.commit()

    #print(type(values)) #tuple

    data = {
    'SearchId': values[0],
    'Sx': values[1],
    'Sy': values[2],
    'Ex': values[3],
    'Ey': values[4],
    'STotalTime': values[5],
    'STotalDistance': values[6],
    'BTotalTime': values[7],
    'BTotalDistance': values[8],
    'Optipath': values[9],
    'Diff': values[10]
}
    data =json.dumps(data)
    print(data)
    response = requests.post("http://192.168.1.71:3500/saveSql", data=data)
    if response.status_code != 200:
        raise HTTPException(status_code=406, detail="Data error")
    print(response)

    sql = f"SELECT * FROM `sidx` WHERE SearchId = {SearchId}"
    cursor.execute(sql)
    result = cursor.fetchone()
    return {201: "Created", "result":result}



## select query

@app.get("/getMongo")
async def getMongo(SearchId: str):  #{"SearchId":"0012"}
    print(SearchId)

    pathS = subwaypath.find_one({"SId": SearchId}, {"_id":0})
    pathB = buspath.find_one({"BId": SearchId}, {"_id":0})
    result = {200: "OK", "result":{"subwaypath": pathS, "buspath": pathB}}
    return result
