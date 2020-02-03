from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render
from pymongo import MongoClient
from . import models
from bson.objectid import ObjectId
import bcrypt
import json, requests
import gridfs
import sys
import datetime, time
import jwt
import pickle
from ftplib import FTP 
from io import BytesIO


client = MongoClient("mongodb://admindbtest:pFkg52L7Bffkdt95@18.140.63.5:27017/test_database")
secretKey = "Ki6wt83A5txZCX0FV0gbtuDazhhgFwd4"

def validate_token(request):
    if not request or 'Bearer' not in request:
        return False

    split = request.split(' ')
    dbadmin = client['test_database']
    decode_data = jwt.decode(split[1], secretKey, algorithms=['HS256'])
    mac = decode_data['connecteddevices']
    user = decode_data['username']
 
    macaddress = []
    cek = dbadmin['accounts_customuser'].find_one({"username": user})
    data = json.loads(cek['devicemacs'])
    for d in data:
        macaddress.append(d['macaddress'])

    print("mac = ", macaddress)
    Cmac = macaddress

    if mac == Cmac:
        return True
    else:
        return False

@csrf_exempt
def postData(request):
    print("method postData",file=sys.stderr)
    if request.method == 'POST':
        print("Request method post data",file=sys.stderr)
        token = request.headers.get('Authorization')
        token2 = request.headers
        print(token2,file=sys.stderr)
        if(validate_token(token)):
            pureToken = token.split(' ')
            datas =json.loads(request.body.decode('utf-8'))
            print(datas,file=sys.stderr)
            datajson = json.loads(datas)
            return dataPost(datas, datajson['topic'], pureToken[1]) 
    return HttpResponse('/api/post')

def validate_topic(topic, token):
    btoken = token.encode('utf-8')
    stoken =  str(btoken)
    db = client['test_database']
    topics = db["topics"]
    validate = topics.find_one({'apiendpoint': topic, 'jwt': stoken}, {"_id" : 1})
    if (validate):
        # print("masuk if validate topic")
        return True
    else:
        # print("masuk else validate topic")
        return False

def isJson(data):
    try:
        json_object = json.loads(data)
        return True
    except TypeError:
        return True
    except ValueError:
        return False

def checkFormat(data):
    dict1 = json.loads(data)
    dict2 = dict1['payload']
    if "files" in dict2:
        payloads = json.loads(data)
        if((payloads['payload']['files'])):
            return "file"
        else:
            return "raw"
    elif isJson(data):
        return "json"
    else:
        return "raw"

def synchronizeSizeEntry(dateTopic, datenow):
    db = client['test_database']
    mycolDate = db[dateTopic]
    check = mycolDate.find({"date": datenow}).distinct("entry")[0]
    if check == 0:
        mycolDate.update({"date": datenow}, {"$set": {'entry': 1}})
    else:
        getCount = mycolDate.find({'date': datenow}).distinct("entry")
        totalEntrty = getCount[0] + 1
        mycolDate.update({'date': datenow}, {"$set": {"entry": totalEntrty}})

def dataPost(datas, topic, token):
    topics = topic.split('/')[1]

    if(validate_topic(topic, token)):

        dbadmin = client['test_database']
        formats = checkFormat(datas)

        id_user = dbadmin['topics'].find({"apiendpoint": topic}).distinct("user_id")[0]
        database_name = dbadmin['accounts_customuser'].find({"id": id_user}).distinct("username")[0].encode("ascii","replace")
        db_decode = database_name.decode('utf-8')
        
        namecol = str(db_decode)
        colUser = dbadmin[namecol]
        dateTopic = dbadmin['date'+topics]
        datenow = datetime.datetime.now().strftime("%d"+"-"+"%m"+"-"+"%Y")
        checkDate = dateTopic.find_one({"date": datenow}, {"_id" : 1})
        
        if(formats == "json"):
            if checkDate is None:
                dateTopic.insert({"date" : datenow, "entry" : 0})
            dataloads = json.loads(datas)
            # print("data = ", dataloads)
            colUser.insert(dataloads)
            mycolDate = 'date'+topics
            synchronizeSizeEntry(mycolDate, datenow)
            return HttpResponse("sys JSON data saved in MongoDB")

        elif(formats == "file"):
            data1 = json.loads(datas)

            #via flask handler
            # r = requests.post(
            #     "http://127.0.0.1:5000/api/file_rules1", 
            #     json = json.dumps(data1), 
            #     headers = {
            #         'Content-type': 'application/json; charset=UTF-8',
            #         'Authorization': "Bearer {}".format(token)}
            # )
            # print("sended")

            #direct ot ftp
            pick = data1['payload']["files"].encode('utf-8')
            filename = data1['payload']["filename"]
            filenameSaved = namecol + "_" + filename 
            files = pickle.loads(pick, encoding='bytes')
            print("masih bisa ga")
            host = "18.140.63.5"
            ftp = FTP(host)
            ftp.set_debuglevel(2)
            ftp.login(user='ptriot-ex', passwd = 'ftp-ptriot-ex')
            ftp.cwd("files/")
            ftp.set_pasv(True)
            ftp.pwd()
            # print("masuk file ga", ftp.pwd())
            myfile = BytesIO(files)
            ftp.storbinary('STOR %s' % filenameSaved, myfile)

            return HttpResponse("sys FILE data saved in Directory")
    else:
        return HttpResponse("error : Wrong topic or topic is unregistered")


def index(request):
    return render(request, 'login/login.html')

def userHome(request):
    return render(request, 'login/home.html')

def registerTopic(request):
    return render(request, 'login/registerTopic.html')

def userShowData(request):
    return render(request, 'login/userShowData.html')

def userSendData(request):
    return render(request, 'login/userSendData.html')


