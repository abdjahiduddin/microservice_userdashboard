from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
# from ast import literal_eval
import sys
from pymongo import MongoClient
from django.conf import settings

#Library for Heart Rate Analytic
from datetime import datetime

# FOR MICROSERVICE HEART RATE ANALYTIC
except_id = {"_id": 0}

# Create your views here.

def connect():
	hostaddress = settings.DB_ADDR
	hostport = settings.DB_PORT
	dbname = settings.DB_NAME

	try:
		client = MongoClient('mongodb://%s:%s/%s'\
				%(hostaddress,hostport,dbname))
	except Exception as e:
		print('Exception occured when connecting to mongo: ',e)

	db = client[dbname]
	return db

# API FOR HEART RATE ANALYTIC
@csrf_exempt
def get_time(requests):
    print("File : Views, Function : get_time",file=sys.stderr)
    if requests.method=="POST":
        dbadmin = connect()
        data = json.loads(requests.body.decode('utf-8'))
        if type(data) is str:
            data = json.loads(data)
        uid = data["uid"]
        find = {
            "id" : float(uid)
        }
        user_exist = dbadmin["accounts_customuser"].find_one(find, except_id)
        data_user = ""
        # If user found
        if user_exist:
            user = user_exist
            # Save other user information to session
            profile_user = {
                "date_joined" : user["date_joined"].strftime("%a, %d %b %Y %H:%M:%S"),
                "username" : user["username"],
                "age" : user["age"],
                "body_height" : user["body_height"],
                "body_weight" : user["body_weight"]
            }
            data_user = {
                "profile": profile_user,
                "time": {
                    "created": user["date_joined"].strftime("%Y-%m-%d"),
                    "now": datetime.now().strftime("%Y-%m-%d")
                },
                "divider_range": {
                    "resting": create_divider(0, int(user["age"])),
                    "exercising": create_divider(1, int(user["age"]))
                }
            }
        payload = {
            "data_user" : data_user
        }
        payload = json.dumps(payload)
    return HttpResponse(payload, content_type='application/json')

# API FOR HEART RATE ANALYTIC
def create_divider(activity, age):
    divider_range = {}

    if activity == 0:
        divider_range["low"] = 60
        divider_range["high"] = 100
    else:
        # Calculate max heart rate
        heart_rate_max = 208 - (0.7 * int(age))

        divider_range["low"] = int(heart_rate_max * 0.5)
        divider_range["high"] = int(heart_rate_max * 0.9)

    return divider_range

# API FOR GATEWAY
@csrf_exempt
def validate_token(requests):
    print("File : Views, Function : validate_token ",file=sys.stderr)
    if requests.method=="POST":
        dbadmin = connect()
        data = json.loads(requests.body.decode('utf-8'))
        if type(data) is str:
            data = json.loads(data)
        user = data["user"]
        cek = dbadmin['accounts_customuser'].find_one({"username": user})
        # payload  = {
        #     "user" : cek
        # }
        data = json.loads(cek['devicemacs'])
        payload = {
            "data" : data
        }
        payload = json.dumps(payload)
    return HttpResponse(payload, content_type='application/json')

# API FOR GATEWAY
@csrf_exempt
def validate_topic(requests):
    print("File : Views, Function : validate_topic ",file=sys.stderr)
    if requests.method=="POST":
        db = connect()
        topics = db["topics"]
        data = json.loads(requests.body.decode('utf-8'))
        if type(data) is str:
            data = json.loads(data)
        stoken = data["stoken"]
        topic = data["topic"]
        validate = topics.find_one({'apiendpoint': topic, 'jwt': stoken}, {"_id" : 1})
        if (validate):
            # print("masuk if validate topic")
            status = True
        else:
            # print("masuk else validate topic")
            status = False
        payload = {
            "status" : status
        }
        payload = json.dumps(payload)
    return HttpResponse(payload, content_type='application/json')        

# API FOR GATEWAY
@csrf_exempt
def get_id_name(requests):
    print("File : Views, Function : get_id_name ",file=sys.stderr)
    if requests.method=="POST":
        dbadmin = connect()
        data = json.loads(requests.body.decode('utf-8'))
        if type(data) is str:
            data = json.loads(data)
        topic = data["topic"]
        id_user = dbadmin['topics'].find({"apiendpoint": topic}).distinct("user_id")[0]
        database_name = dbadmin['accounts_customuser'].find({"id": id_user}).distinct("username")[0].encode("ascii","replace") 
        db_decode = database_name.decode('utf-8')
        namecol = str(db_decode)
        payload = {
            "database_name" : namecol
        }
        payload = json.dumps(payload)
    return HttpResponse(payload, content_type='application/json') 
