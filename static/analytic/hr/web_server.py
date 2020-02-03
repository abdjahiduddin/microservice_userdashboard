import os
import ast
import json
import psutil
import threading
import logging
from datetime import datetime
from flask import Flask, render_template, request, session, url_for, redirect, jsonify
from visualizer import main_process as create_graph
# from cloud import authenticate_users
from mongodb import connections, nDB
from analytic import main_process as listen_raw 


# Define web application
app = Flask("Web Apps")
app.secret_key = "always secret"
host = '0.0.0.0'
port = 8888
api_folder = os.getcwd() + "/static/api/"
except_id = {"_id": 0}


# Main process for web server component
# Start web server
def main_process():
    # Run web application in port 8888 of all interface
    print("[Web Server] * Flask server run on http://" +
          host + ":" + str(port) + "/ (Press CTRL+C to quit)")
    listen_raw()
    app.run(host=host, port=port)

# def analytic_thread():
#     thread = threading.Thread(target=listen_raw)
#     thread.setDaemon(True)
#     thread.start()


@app.route("/", methods=["GET"])
def landing():
    user = get_time("azzu", "d8:c4:e9:75:93:22")
    return render_template("home.html", user=user, status="NOPE")

# Route for find trend process
@app.route("/trend/process", methods=["POST"])
def find_trend():
    # Get HTML form
    listen_raw()
    form = form_to_dict([])

    user = get_time("azzu", "d8:c4:e9:75:93:22")
    # Define some necessaries
    info = {
        "trend": {
            "type": form["type"]
        },
        "user": {
            "username": "azzu",
            "age": "22",
            "device": "d8:c4:e9:75:93:22",
            "divider_range": user["divider_range"]
        }
    }

    # Define trend result
    trend_result = {
        "detail": {},
        "filename": {},
        "access_time": str(datetime.now()),
        "type": info["trend"]["type"],
        "html_format": {
            "div": {},
            "illustration": {}
        },
        "type": form["type"]
    }

    # If looking for trend type track
    if info["trend"]["type"] == "track":
        # Define track type query
        check_trend = {
            "profile.username": info["user"]["username"],
            "profile.device": info["user"]["device"],
            "trend.type": info["trend"]["type"]
        }

        # Check trend
        trend_exist = get_data_db_hr("alice",check_trend)

        # If trend exist
        if trend_exist:
            # Define trend
            trend = trend_exist

            # Define trend date and date format
            info["trend"]["date"] = trend["trend"]["time"]
            info["trend"]["date_format"] = "%a, %d %b %Y %H:%M:%S"

            # Add trend result
            activity = parse_activity(int(trend["trend"]["activity"]))
            divider_range = user["divider_range"][activity]
            trend_result["detail"][activity], trend_result["html_format"]["illustration"][activity] = explore_trend(
                divider_range, trend)
        # If trend not found
        else:
            # Define trend date and date format
            info["trend"]["date"] = datetime.now()
            info["trend"]["date_format"] = "Not Found"

            # Add trend not found result
            trend_result["detail"]["not found"] = "No data could be found."

        # Define track type div format
        div_format = {
            "outer": "col-sm-12",
            "inner1": "col-sm-3",
            "inner2": "col-sm-9"
        }
    # If looking for trend type other than track (yearly, monthly, or daily)
    else:
        # Split by "-" --> parse to int --> create list -> define date
        form_date = list(map(int, form['date'].split("-")))

        # Define trend date, date_format, and file_format by trend_type
        if info["trend"]["type"] == "yearly":
            info["trend"]["date"] = datetime(form_date[0], 1, 1)
            info["trend"]["date_format"] = "%Y"
        elif info["trend"]["type"] == "monthly":
            info["trend"]["date"] = datetime(form_date[0], form_date[1], 1)
            info["trend"]["date_format"] = "%b %Y"
        else:
            info["trend"]["date"] = datetime(
                form_date[0], form_date[1], form_date[2])
            info["trend"]["date_format"] = "%a, %d %b %Y"

        # Define other than track type query
        check_trend = {
            "profile.username": info["user"]["username"],
            "profile.device": info["user"]["device"],
            "trend.type": info["trend"]["type"],
            "trend.time": info["trend"]["date"]
        }

        # For resting (0) and excercising (1) activity
        for activity in [0, 1]:
            # Define activity in number and string
            info["trend"]["act(num)"] = activity
            info["trend"]["act(str)"] = parse_activity(activity)
            check_trend["trend.activity"] = info["trend"]["act(num)"]

            # Check trend
            trend_exist = get_data_db_hr("alice",check_trend)

            # If trend exist
            if trend_exist:
                # Define trend
                trend = trend_exist
                # Add trend result
                divider_range = user["divider_range"][info["trend"]
                                                      ["act(str)"]]
                trend_result["detail"][info["trend"]["act(str)"]], trend_result["html_format"][
                    "illustration"][info["trend"]["act(str)"]] = explore_trend(divider_range, trend)
                # Define and add trend filename
                trend_result["filename"][info["trend"]["act(str)"]] = "visual/" + \
                    info["user"]["username"] + "_" + \
                    info["trend"]["act(str)"] + ".svg"
                # Create visualization
                create_graph(info)
            else:
                # Add trend not found result
                trend_result["detail"][info["trend"]
                                       ["act(str)"]] = "No data could be found for " + info["trend"]["act(str)"] + " activity."

        # Define other than track type div format
        div_format = {
            "outer": "col-sm-5",
            "inner1": "col-sm-12",
            "inner2": "col-sm-12"
        }

    # Add trend time range and div format
    trend_result["time_range"] = info["trend"]["date"].strftime(
        info["trend"]["date_format"])
    trend_result["html_format"]["div"] = div_format
    print("File : Web Server, Function Find Trend")
    return render_template("home.html", user=user, trend=trend_result, status="OK")


def get_time(username, device):
    find = {
        "username": username,
        "device": device
    }
    user_exist = connections["user"].find_one(find, except_id)

    data_user = ""

    # If user found
    if user_exist:
        user = user_exist
        # Save other user information to session
        data_user = {
            "profile": user,
            "time": {
                "created": user["created"].strftime("%Y-%m-%d"),
                "now": datetime.now().strftime("%Y-%m-%d")
            },
            "divider_range": {
                "resting": create_divider(0, int(user["age"])),
                "exercising": create_divider(1, int(user["age"]))
            }
        }
    return data_user


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

# Change form to dictionary with exclude feature


def form_to_dict(excludes):
    form = request.form.to_dict()
    # Exclude some field in form
    for exclude in excludes:
        form.pop(exclude)
    return form

# Redirect page with cookies function


def redirect_page(page, variables_to_cookies):
    # Define location to landing zone
    response = redirect(url_for("landing", page=page))
    # Change all needed variables to cookies
    for key, value in variables_to_cookies.items():
        response.set_cookie(key, str(value), max_age=1)
    # Return redirect function and it's cookies
    return response


def parse_activity(activity_number):
    if activity_number == 0:
        return "resting"
    else:
        return "exercising"

# Explore trend necessary information


def explore_trend(divider_range, trend):
    # Define necessaries
    avg_hr = trend["trend"]["heart_rate"]["average"]
    status = trend["trend"]["status"]
    space = "        "

    # Define trend detail
    color, condition, reason, solution = explore_detail(status)
    detail = {
        "status": status,
        "color": color,
        "condition": condition,
        "reason": reason,
        "solution": solution,
        "average": avg_hr
    }

    # Define trend illustration
    low, middle, high, info = illustrate(status, divider_range, avg_hr)
    illustration = {
        "line": low + space + middle + space + high,
        "info": info
    }
    # Return trend detail and illustration
    return detail, illustration

# Explore trend detail


def explore_detail(status):
    # Slow status trend detail
    if status == "slow":
        # Want to warn user (font color is red and condition not healthy)
        # that their heart rate is conditioned as slow heart rate
        solution = "is a article summary about slow heart rate, read it for better understanding."
        return "red", "may not healthy", "slower than", solution
    # Fast status trend detail
    elif status == "fast":
        # Want to warn user (font color is red and condition not healthy)
        # that their heart rate is conditioned as fast heart rate
        solution = "is a article summary about fast heart rate, read it for better understanding."
        return "red", "may not healthy", "faster than", solution
    # Normal status trend detail
    else:
        # Want to inform user (font color is green and condition healthy)
        # that their heart rate is conditioned as normal heart rate
        solution = "No treatment needed. Keep going!!!"
        return "green", "healthy", "within", solution


# Illustrate trend
def illustrate(status, divider_range, heart_rate):
    space = "                    "
    # Slow status trend illustration
    if status == "slow":
        # Initialize slow illustration
        # their heart rate -+- minimum divider -+- maximum divider
        #    [yours]
        return str(heart_rate), str(divider_range["low"]), str(divider_range["high"]), "[yours]" + space
    # Fast status trend illustration
    elif status == "fast":
        # Initialize fast illustration:
        # minimum divider -+- maximum divider -+- their heart rate
        #                                            [yours]
        return str(divider_range["low"]), str(divider_range["high"]), str(heart_rate), space + "[yours]"
    # Normal status trend illustration
    else:
        # Initialize fast illustration:
        # minimum divider -+- their heart rate -+- maximum divider
        #                          [yours]
        return str(divider_range["low"]), str(heart_rate), str(divider_range["high"]), "[yours]"


def get_data_db_hr(user, info):
    connection = nDB[user]
    if info["trend.type"] == "track":
        cursor = connection.aggregate(
            [
                {"$match": {"analytic_type": "heart_rate"}},
                {"$project": {
                    "trend": {"$filter": {
                        "input": '$trend',
                        "as": 'trend',
                        "cond": {"$and": [
                            {"$eq": ['$$trend.profile.device', info["profile.device"]]},
                            {"$eq": ['$$trend.trend.type', info["trend.type"]]}
                        ]
                        }
                    }},
                    "_id": 0
                }},
                {"$sort": {"heart_rate.trend.time": -1}}
            ]
        )
    else:
        cursor = connection.aggregate(
            [
                {"$match": {"analytic_type": "heart_rate"}},
                {"$project": {
                    "trend": {"$filter": {
                        "input": '$trend',
                        "as": 'trend',
                        "cond": {"$and": [
                            {"$eq": ['$$trend.profile.device', info["profile.device"]]},
                            {"$eq": ['$$trend.trend.type', info["trend.type"]]},
                            {"$eq": ['$$trend.trend.time', info["trend.time"]]},
                            {"$eq": ['$$trend.trend.activity', info["trend.activity"]]}                            
                        ]
                        }
                    }},
                    "_id": 0
                }},
                {"$sort": {"heart_rate.trend.time": -1}}
            ]
        )

    data = list(cursor)
    data = data[0]
    if len(data['trend']) == 0:
        trend = False
    else:
        trend = data['trend'][0]
    return trend


main_process()
