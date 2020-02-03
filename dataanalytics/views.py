from django.shortcuts import render
from django.http import HttpResponse
import requests
import json
import numpy as np
import pymongo
from bson.objectid import ObjectId
from django.conf import settings

hostaddress = settings.DB_ADDR
hostport = settings.DB_PORT
dbname = settings.DB_NAME

gtwhost = settings.GTW_HOST
gtwport = settings.GTW_PORT

hrahost = settings.HRA_HOST
hraport = settings.HRA_PORT

# Versi Development
client2 = pymongo.MongoClient('mongodb://%s:%s/%s'\
	%(hostaddress,hostport,dbname))
nDB = client2[dbname]

client = pymongo.MongoClient('mongodb://%s:%s/%s'\
	%(hostaddress,hostport,dbname))
db = client[dbname]


def homepage(response):
    args = get_topics(response)
    return render(response, "main/index.html", args)


def arrhytmia(response):
    if response.method == "POST":
        args = check_topic_data(response)
        if args["error"] == "true":
            return render(response, "main/index.html", args)
        else:
            topic = args["topic"]
            args = arrhytmia_getdata(response, args["topic"])
            key = arrhytmia_get_history(response, topic)
            args["keys"] = key
            return render(response, "main/ecgdashboard.html", args)
            # arrhytmia_process(response)


def arrhytmia_get_history(response, topic):
    data = response.user
    user = data.username
    conn = db[user]
    history = conn.find({
        "analytic_type": "arrhytmia",
        "topic": topic
    }, {
        "analytic_type": 0,
        "arrhytmia": 0,
        "topic": 0,
        "created": 0
    })
    key = {}
    historys = list(history)
    if len(historys) > 0:
        for history in historys:
            key[history["key"]] = history["_id"]
    return key


def arrhytmia_getdata(response, topic):
    data = response.user
    user = data.username
    conn = db[user]

    args = {}
    args["topic"] = topic
    args["user"] = user
    filter = {
        "status": {
            "$exists": False
        },
        "analytic_type": {
            "$exists": False
        },
        "payload.ecg": {
            "$exists": True
        },
        "topic": topic
    }
    count = conn.find(filter).count()
    if count > 499:
        start = conn.find(filter).sort("_id", 1).limit(1)
        datas = list(start)[0]
        idstart = datas['_id']
        start = datas['time']
        end = conn.find(filter).sort("_id", -1).limit(1)
        datae = list(end)[0]
        idend = datae['_id']
        end = datae['time']
        args["start"] = start
        args["end"] = end
        args["idstart"] = idstart
        args["idend"] = idend
        args["error"] = ""
    else:
        args["start"] = ""
        args["end"] = ""
        args["idstart"] = ""
        args["idend"] = ""
        args["error"] = "true"
        args["message"] = "There is not enough data to clasify!"

    return args


def arrhytmia_history(response):
    if response.method == "POST":
        data = response.user
        username = data.username
        age = data.age
        topic = response.POST.get("topic")
        key = response.POST.get("selectdata")
        uid = response.POST.get(key)
        key_split = key.split(" : ")
        start = key_split[0]
        end = key_split[1]
        args = get_hasil(username, uid, age)
        args["topic"] = topic
        args["start"] = start
        args["end"] = end
    return render(response, "main/details.html", args)


def arrhytmia_process(response):
    if response.method == "POST":
        data = response.user
        username = data.username
        age = data.age
        topic = response.POST.get("topic")
        start = response.POST.get("idstart")
        end = response.POST.get("idend")
        args = {
            "user": username,
            "start": start,
            "end": end,
            "topic": topic
        }
        conn = requests.post(
            "http://3.1.49.16/analytic/arrhytmia",
            json=json.dumps(args),
            headers={
                'Content-type': 'application/json; charset=UTF-8'}

        )
        data = json.loads(conn.text)
        if data['status'] == "OK":
            args = get_hasil(username, data['id'], age)
            args["topic"] = topic
            args["start"] = start
            args["end"] = end
            return render(response, "main/details.html", args)
        else:
            return render(response, "main/404.html")


def heart_rate(response):
    if response.method == "POST":
        args = check_topic_data(response)
        if args["error"] == "true":
            return render(response, "main/index.html", args)
        else:
            args = heart_rate_process(response, args["topic"])
            return render(response, "main/heart_rate/home.html", args)
            # payload  = {
            #     "status" : "OK",
            # }
            # payload = json.dumps(payload)
            # return HttpResponse(payload, content_type='application/json')


def heart_rate_process(response, topic):
    data = response.user
    username = data.username
    uid = data.id
    age = data.age
    args = {
        "user": username,
        "uid": uid,
        "age": age,
        "topic": topic
    }
    conn = requests.post(
        "http://{}:{}/analytic/hr/dashboard".format(hrahost,hraport),
        json=json.dumps(args),
        headers={
            'Content-type': 'application/json; charset=UTF-8'}
    )
    data = json.loads(conn.text)
    print(data)
    print(type(data))
    args["created"] = data['user']['time']['created']
    args["now"] = data['user']['time']['now']
    args["status"] = data['status']
    args["topic"] = topic

    return args


def trend_process(response):
    data = {}
    args = {}
    datauser = response.user
    username = datauser.username
    age = datauser.age
    uid = datauser.id
    data['user'] = username
    data['age'] = age
    data['uid'] = uid
    if response.method == "POST":
        data['type'] = response.POST.get("type")
        data['topic'] = response.POST.get("topic")
        if data['type'] == "track":
            data['date'] = ""
        else:
            data['date'] = response.POST.get("date")
        conn = requests.post(
            "http://{}:{}/analytic/hr/process".format(hrahost,hraport), 
            json=json.dumps(data),
            headers={
                'Content-type': 'application/json; charset=UTF-8'}
        )
        data = json.loads(conn.text)
        args["user"] = data['user']
        args["status"] = data['status']
        args["trend"] = data['trend']
        args["topic"] = response.POST.get("topic")
    return render(response, "main/heart_rate/home.html", args)


def article_summaries(response, status):
    if status == "slow":
        return render(response, "main/heart_rate/article_summaries/slow.html")
    else:
        return render(response, "main/heart_rate/article_summaries/fast.html")


def get_topics(response):
    userdata = response.user
    uid = userdata.id
    topics_conn = nDB["topics"]
    topics = topics_conn.find({
        "user_id": uid
    })
    payload = []
    args = {}
    for topic in topics:
        payload.append(topic['apiendpoint'])
    args['topics'] = payload
    args['error'] = ""
    args['error_msg'] = ""
    return args


def check_topic_data(response):
    user = str(response.user)
    analytic_type = response.POST.get("analytictype")
    topic = response.POST.get("selecttopic")

    if topic == "0":
        args = get_topics(response)
        args['error'] = "true"
        args['error_msg'] = "Please select topic to analyze!!!"
        print("topic 0")
    else:
        args = get_topics(response)
        payload = {
            "user" : user,
            "analytic_type" : analytic_type,
            "topic" : topic
        }

        conn = requests.post(
            "http://{}:{}/api/countdata".format(gtwhost,gtwport),
            json=json.dumps(payload),
            headers={
                'Content-type': 'application/json; charset=UTF-8'
            }
        )

        if conn.status_code:
            data = json.loads(conn.text)
            data_length = data["data_length"]
        else:
            data_length = 0
        
        if data_length <= 0:
            args['error'] = "true"
            args['error_msg'] = "There is no data to analyze!!!"
            # if analytic_type == "arrhytmia":
            #     args['error'] = "true"
            #     args['error_msg'] = "There is no data to analyze!!!"
            #     print("topic 0 arrhytmia")
            # else:
            #     args['error'] = "true"
            #     args['error_msg'] = "There is no data to analyze!!!"
            #     print("topic 0 hr")
    args["topic"] = topic
    return args


def get_hasil(nama, id, umur):
    connection = nDB[nama]
    query_result = connection.find_one({"_id": ObjectId(id)})
    # query_result = connection.find(
    #     {"analytic_type": "arrhytmia"},
    #     {"analytic_type": 0, "_id": 0, "processed": 0}
    # )

    # query_result = list(query_result)[0]['arrhytmia']
    data = query_result["arrhytmia"]['data']
    hasil = query_result["arrhytmia"]['hasil']

    umur = umur
    created = query_result["created"]
    created = created.strftime("%a, %d %b %Y %H:%M:%S")

    ecg = data["ecg"]
    ts = data["timeseries"]
    ecg_ts = []
    # ts + ecg
    for count, i in enumerate(ecg):
        ecg_ts.append([ts[count], i])

    filtered = data["filtered"]
    filtered_ts = []
    # ts + filtered
    for count, i in enumerate(filtered):
        filtered_ts.append([ts[count], i])

        # hasil
    result = hasil["hasil"]
    PVC = []
    PAB = []
    RBB = []
    LBB = []
    APC = []
    VEB = []
    for key in result.keys():
        if len(result[key]) > 0:
            tmp = result[key]
            for x in tmp:
                if key == "PVC":
                    PVC.append([ts[x[0]], ts[x[1]]])
                elif key == "PAB":
                    PAB.append([ts[x[0]], ts[x[1]]])
                elif key == "RBB":
                    RBB.append([ts[x[0]], ts[x[1]]])
                elif key == "LBB":
                    LBB.append([ts[x[0]], ts[x[1]]])
                elif key == "APC":
                    APC.append([ts[x[0]], ts[x[1]]])
                elif key == "VEB":
                    VEB.append([ts[x[0]], ts[x[1]]])
    result = {
        "APC": APC,
        "LBB": LBB,
        "PAB": PAB,
        "PVC": PVC,
        "RBB": RBB,
        "VEB": VEB
    }

    # get value ts by rpeaks index
    rpeaks = hasil["rpeaks"]
    rpeaks = np.array(rpeaks)
    ts_tmp = np.array(ts)
    rpeaks = ts_tmp[rpeaks]
    rpeaks = rpeaks.tolist()

    hr = hasil["heart_rate"]
    hr_template = hasil["hr_template"]

    tmp = {
        "status": "OK",
        "result": {
            "nama": nama,
            "umur": umur,
            "data": ecg_ts,
            "hasil": result,
            "filtered": filtered_ts,
            "hr_template": hr_template,
            "rpeaks": rpeaks,
            "hr": hr
        }
    }

    args = {}

    args['data'] = ecg_ts
    args['filtered'] = filtered_ts
    args['hasil'] = result
    args['hr'] = hr
    args['hr_template'] = hr_template
    args['rpeaks'] = rpeaks
    args['nama'] = nama
    args['umur'] = umur
    args['created'] = created

    return args


def get_data_ecg(user):
    data = False
    connection = db[user]
    print("Connected to collection : ", user)

    id = connection.find({"payload.ecg": {"$exists": True}}, {"payload": 0})

    id = list(id)
    if id:
        id = id[0]['_id']
        cursor = connection.aggregate(
            [
                {"$match": {"_id": ObjectId(id)}},
                {"$project": {
                    "raw": '$payload.ecg',
                    "_id": 0
                }}
            ]
        )
        data = list(cursor)
        print("Getting payload from collection")
        data = data[0]['raw']
    return data


# Dari JAY Versi Lama 2
# def homepage(response):
#     #urlAnalytic = "http://3.1.218.130:5000/"

#     #responAnalytic = requests.request("GET", urlAnalytic)
#     #responAnalytic = responAnalytic.json()
#     #if responAnalytic['status'] == "OK":
#     #    args = {}
#     #    data = []
#     #    col = db["pasien"]
#     #    pasien = col.find({})
#     #    for i in pasien:
#     #        tmp = {
#     #            "nama": i["nama"],
#     #            "umur": i["umur"]
#     #        }
#     #        data.append(tmp)
#     #    args['data'] = data
#     #    return render(response, "main/index.html", args)
#     #else:
#     #    return render(response, "main/404.html")
#     # args = {}
#     # data = []
#     # col = db["pasien"]
#     # pasien = col.find({})
#     # for i in pasien:
#     #     tmp = {
#     #         "nama": i["nama"],
#     #         "umur": i["umur"]
#     #     }
#     #     data.append(tmp)
#     # args['data'] = data
#     # return render(response, "main/index.html", args)
#     payload = response.user
#     payload = json.dumps({
#         "id" : payload.id
#     })
#     return HttpResponse(payload, content_type='application/json')

# def analytic(response, username):
#     urlAnalytic = "http://3.1.218.130:5000/requestAnalysis/{}".format(username)
#     responAnalytic = requests.request("GET", urlAnalytic)
#     responAnalytic = responAnalytic.json()
#     if responAnalytic['status'] == "OK":
#         args = getHasil(username)
#         return render(response, "main/details.html", args)
#     else:
#         return render(response, "main/404.html")

# def getHasil(name):
#     errorMsg = ""
#     count = 0

#     col = db["data"]
#     col1 = db["pasien"]
#     col2 = db["hasil"]

#     check = []


#     check.append(col.find({"nama":name}).count())
#     check.append(col1.find({"nama":name}).count())
#     check.append(col2.find({"nama":name}).count())
#     if check.count(1) < 3:
#         for count,i in enumerate(check):
#             if i == 0:
#                 if count == 0:
#                     errorMsg = errorMsg + " Data in Data Collection Not Found."
#                 elif count == 1:
#                     errorMsg = errorMsg + " Data in Pasien Collection Not Found."
#                 else:
#                     errorMsg = errorMsg + " Data in Hasil Collection Not Found."
#         tmp = {
#             "status":"ERROR",
#             "message":errorMsg
#         }

#     else:
#         data = col.find_one({"nama":name})
#         pasien = col1.find_one({"nama":name})
#         hasil = col2.find_one({"nama":name})

#         nama = name
#         umur = pasien["umur"]
#         ecg = data["data"]
#         ts = data["timeseries"]
#         ecg_ts = []
#         # ts + ecg
#         for count,i in enumerate(ecg):
#             ecg_ts.append([ts[count],i])

#         filtered = data["filtered"]
#         filtered_ts = []
#         # ts + filtered
#         for count,i in enumerate(filtered):
#             filtered_ts.append([ts[count],i])

#         # hasil
#         result = hasil["hasil"]
#         PVC = []
#         PAB = []
#         RBB = []
#         LBB = []
#         APC = []
#         VEB = []
#         for key in result.keys():
#             if len(result[key]) > 0 :
#                 tmp = result[key]
#                 for x in tmp:
#                     if key == "PVC":
#                         PVC.append([ts[x[0]],ts[x[1]]])
#                     elif key == "PAB":
#                         PAB.append([ts[x[0]],ts[x[1]]])
#                     elif key == "RBB":
#                         RBB.append([ts[x[0]],ts[x[1]]])
#                     elif key == "LBB":
#                         LBB.append([ts[x[0]],ts[x[1]]])
#                     elif key == "APC":
#                         APC.append([ts[x[0]],ts[x[1]]])
#                     elif key == "VEB":
#                         VEB.append([ts[x[0]],ts[x[1]]])
#         result = {
#             "APC": APC,
#             "LBB": LBB,
#             "PAB": PAB,
#             "PVC": PVC,
#             "RBB": RBB,
#             "VEB": VEB
#             }

#         #get value ts by rpeaks index
#         rpeaks = hasil["rpeaks"]
#         rpeaks = np.array(rpeaks)
#         ts_tmp = np.array(ts)
#         rpeaks = ts_tmp[rpeaks]
#         rpeaks = rpeaks.tolist()

#         hr = hasil["heart_rate"]
#         hr_template = hasil["hr_template"]

#         tmp = {
#             "status":"OK",
#             "result":{
#                 "nama":nama,
#                 "umur":umur,
#                 "data":ecg_ts,
#                 "hasil":result,
#                 "filtered":filtered_ts,
#                 "hr_template":hr_template,
#                 "rpeaks": rpeaks,
#                 "hr":hr
#             }
#         }
#     args = {}

#     args['data'] = ecg_ts
#     args['filtered'] = filtered_ts
#     args['hasil'] = result
#     args['hr'] = hr
#     args['hr_template'] = hr_template
#     args['rpeaks'] = rpeaks
#     args['nama'] = nama
#     args['umur'] = umur

#     return args
# END dari JAY Versi Lama 2


# DARI JAY Versi lama
# def homepage(response):
#     urlStorage = "http://127.0.0.1:5001/getAllName"
#     urlAnalytic = "http://127.0.0.1:5000/"
#     responAnalytic = requests.request("GET", urlAnalytic)
#     responAnalytic = responAnalytic.json()
#     if responAnalytic['status'] == "OK":
#         args = {}
#         responStorage = requests.request("GET", urlStorage)
#         respon = responStorage.json()
#         args['data'] = respon
#         return render(response,"dataanalytics/index.html",args)
#     else:
#         return render(response,"dataanalytics/404.html")

# def analytic(response, username):
#     urlAnalytic = "http://127.0.0.1:5000/requestAnalysis/{}".format(username)
#     responAnalytic = requests.request("GET", urlAnalytic)
#     responAnalytic = responAnalytic.json()
#     if responAnalytic['status'] == "OK":
#         args = getHasil(username)
#         return render(response,"dataanalytics/details.html",args)
#     else:
#         return render(response,"dataanalytics/404.html")


# def getHasil(username):
#     args = {}
#     url = "http://127.0.0.1:5001/getOneData/{}".format(username)
#     respon = requests.request("GET", url)
#     result = respon.json()

#     args['data'] = result['result']['data']
#     args['filtered'] = result['result']['filtered']
#     args['hasil'] = result['result']['hasil']
#     print(args['hasil'])
#     args['hr'] = result['result']['hr']
#     args['hr_template'] = result['result']['hr_template']
#     args['rpeaks'] = result['result']['rpeaks']
#     args['nama'] = result['result']['nama']
#     args['umur'] = result['result']['umur']

#     return args
# #END DARI JAY
