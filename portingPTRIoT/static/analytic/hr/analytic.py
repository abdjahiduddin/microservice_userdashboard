from datetime import datetime
from bson.objectid import ObjectId
from heartrate_classifier import classify, main_process as generate_classifier
from mongodb import connections,nDB
from api import create_file
# from test import runtime

connection = nDB['alice']
# Main process for analytic component
# Listen to raw collection
def main_process():

    # Generate Heart Rate Classifier
    generate_classifier()
    id = connection.find({ "payload": { "$exists": "true" } },{"payload" : 0})

    id = list(id)
    id = id[0]['_id']

    cursor = connection.aggregate(
        [
            {"$match": {"_id": ObjectId(id)}},
            {"$project": {
                "raw": {"$filter": {
                    "input": '$payload.heart_rate',
                    "as": 'raw',
                    "cond": {"$eq": ['$$raw.processed',False]}
                }},
            }},
            {"$sort": {"payload.heart_rate.time": -1}}
        ]
    )

    data = list(cursor)
    data = data[0]
    trends = data['raw']

    if trends:
        for raw in trends:
            # Check trends
            check_trends(raw)

            # Update previous trend in database
            # connections["raw"].update({"_id": ObjectId(raw['_id'])}, {"$set": {"processed": True}})
    print("File : Analytic, Function : main_process ")  



# Create time series (by current time)
def create_series(time):
    time_range = {
        "track": time,
        "hourly": datetime(time.year, time.month, time.day, time.hour, 0, 0),
        "daily": datetime(time.year, time.month, time.day, 0, 0, 0),
        "monthly": datetime(time.year, time.month, 1, 0, 0, 0),
        "yearly": datetime(time.year, 1, 1, 0, 0, 0)
    }
    print("File : Analytic, Function : create_series ") 
    return time_range


# Check trends in database
def check_trends(new_data):
    id = connection.find({ "payload": { "$exists": "true" } },{"payload" : 0})

    id = list(id)
    id = id[0]['_id']

    # Define user information
    user = {
        "username": new_data["username"],
        "age": new_data["age"]
    }

    # Create time series trend
    time_range = create_series(new_data["time"])

    i = 0
    # For each time series trend
    for trend_type, time in time_range.items():
        print(i,"==============================================")
        i = i+1
        # Current trend
        trend = {
            "type": trend_type,
            "activity": new_data["activity"],
            "time": time,
            "heart_rate": int(new_data["heart_rate"]),
            "device": new_data["device"]
        }

        # Check if trend exist
        check_trend = {
            "profile.username": new_data["username"],
            "profile.device": new_data["device"],
            "trend.type": trend_type,
            "trend.activity": new_data["activity"],
            "trend.time": time
        }
        print("Check Trend")
        print(check_trend)
        cursor = connection.aggregate(
            [
                {"$match": {"analytic_type": "heart_rate"}},
                {"$project": {
                    "trend": {"$filter": {
                        "input": '$trend',
                        "as": 'trend',
                        "cond": { "$and" : [
                            {"$eq": ['$$trend.profile.username',check_trend['profile.username']]},
                            {"$eq": ['$$trend.profile.device',check_trend['profile.device']]},
                            {"$eq": ['$$trend.trend.type',check_trend['trend.type']]},
                            {"$eq": ['$$trend.trend.activity',check_trend['trend.activity']]},
                            {"$eq": ['$$trend.trend.time',check_trend['trend.time']]},
                        ]
                        }
                    }},
                }}
            ]
        )
        data = list(cursor)
        data = data[0]
        if len(data['trend']) == 0:
            trend_exist = False
        else:
            trend_exist = data['trend'][0]
        print("Trend")
        print(trend_exist)
        # trend_exist = connections["trend"].find_one(check_trend)
        # print("Trend_exist")
        # print(trend_exist)
        # If trend exist
        if trend_exist:
            print("IF TRUE")
            prev_trend = trend_exist
            update_trend(user, trend, prev_trend)
        else:
            print("IF FALSE")
            create_trend(user, trend)

    ### TESTING ###
    #runtime("end")
    print("File : Analytic, Function : check_trends ")


# Create new trend
def create_trend(user, trend):
    # Constructing trend
    new_trend = {
        "trend": {
            "status": classify(trend["activity"], user["age"], trend["heart_rate"]),
            "type": trend["type"],
            "activity": trend["activity"],
            "time": trend["time"],
            "heart_rate": {
                "data": [trend["heart_rate"]],
                "average": trend["heart_rate"]
            }
        },
        "profile": {
            "device": trend["device"],
            "username": user["username"]
        }
    }
    print("new trend")
    print(new_trend)

    # Insert new trend to database
    # connections["trend"].insert_one(new_trend)
    # print("[Analytic] " + str(new_trend) + " Inserted to Collection: Trend")

    connection.update(
        {"analytic_type" : "heart_rate"},
        {"$push" : {
            "trend": {
                "$each" : [new_trend],
                "$position" : 0
                }
            }
        }
    )


    # Save to file for trend_type track (API)
    # if trend["type"] == "track":
    #     create_file(new_trend)
    print("File : Analytic, Function : create_trend ")


# Update previous trend
def update_trend(user, trend, prev_trend):
    id = connection.find({ "payload": { "$exists": "true" } },{"payload" : 0})
    id = list(id)
    id = id[0]['_id']
    # Recomputing average heart rate
    new_trend = prev_trend["trend"]["heart_rate"]
    new_trend["data"].append(trend["heart_rate"])
    new_trend["average"] = int(sum(new_trend["data"]) / len(new_trend["data"]))

    filter_trend = {
        "trend.trend.status":prev_trend["trend"]["status"],
        "trend.trend.type":prev_trend["trend"]["type"],
        "trend.trend.activity":prev_trend["trend"]["activity"], 
        "trend.trend.time":prev_trend["trend"]["time"]
    }
    updated_trend = {
        "$set": {
            "trend.$.trend.status": classify(prev_trend["trend"]["activity"], user["age"], new_trend["average"]),
            "trend.$.trend.heart_rate.data": new_trend["data"],
            "trend.$.trend.heart_rate.average": new_trend["average"]
        }
    }
    connection.update(filter_trend,updated_trend)

    # print("Update trend")
    # print(updated_trend)
    # print("user")
    # print(user)
    # print("prev trend")
    # print(prev_trend)
    # print("trend")
    # print(trend)

    # print("[Analytic] " + str(prev_trend["_id"]) + " Trend Updated in Collection: Trend")
    print("File : Analytic, Function : update_trend ")

