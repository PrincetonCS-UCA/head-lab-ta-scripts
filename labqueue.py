#===================================================================================
# Unfinished script for tracking Lab TA attendance. 
#===================================================================================
from wsse.client.requests.auth import WSSEAuth
import requests
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime

from subswap.models import Shift
#===================================================================================

username = "cas-princeton-netid"
API_SECRET = "secret"
wsse_auth = WSSEAuth(username, API_SECRET)
base_url = "https://www.labqueue.io/api/v1/"
#===================================================================================

def get_requests(netid):
    """
    Input:
        netid: str

    Output:
        "results":[
                    {
                        "pk":61862,
                        "author_full_name":"Claire + Anna",
                        "author_netid":"ck2887",
                        "location":"Lewis 122",
                        "in_person":true,
                        "course":"intro-cs-lab_cos-126",
                        "description":"Error with StingBuilder formatting",
                        "time_created":"2022-11-18T19:01",
                        "acceptor_netid":"mmir",
                        "time_accepted":"2022-11-18T19:05",
                        "closer_netid":"mmir",
                        "time_closed":"2022-11-18T19:22"
                    },
                    ...
                ]

    Gets all the request fom the queue from the current semester.
    """
    time = "2022-08-01T00:00"
    payload = {"accepted_by": netid, "accepted_after": time}
    result = requests.get(base_url + "requests/query",
                          auth=wsse_auth, params=payload).json()

    curr_sem = (9, 12) if 9 <= datetime.today().month <= 12 else (2, 5)
    result["results"] = [x for x in result["results"]
                         if curr_sem[0] <= datetime.strptime(x["time_accepted"], '%Y-%m-%dT%H:%M').month <= curr_sem[1]]

    return result


def attendance(netid):
    """
    Input:
        netid: str
        shiftid: int

    Output:
        {
            "COS126, Wednesday, 7pm - 9pm": ["11/13/2022, 7pm - 9pm", "11/18/2022, 9pm - 11pm", ...],
            "COS226/217, Sunday, 9pm - 11pm": [*list of dates*]

    Gets all the unexcused absenses (no request posted) of the worker from the current semester.
    """


def time_spent_per_request(netid, starttime, endtime):
    """
    Inputs:
        netid: str
        starttime, endtime: DateTime object -> "yyyy-mm-ddThh:mm"

    Result input format:
    {
        "count":6,
        "next":null,
        "previous":null,
        "results":[
                    {
                        "pk":61862,
                        "author_full_name":"Claire + Anna",
                        "author_netid":"ck2887",
                        "location":"Lewis 122",
                        "in_person":true,
                        "course":"intro-cs-lab_cos-126",
                        "description":"Error with StingBuilder formatting",
                        "time_created":"2022-11-18T19:01",
                        "acceptor_netid":"mmir",
                        "time_accepted":"2022-11-18T19:05",
                        "closer_netid":"mmir",
                        "time_closed":"2022-11-18T19:22"
                    },
                    ...
                ]
    }

    Result output format:
    {
        "overall": {"count: 10, "average_minutes_per_request": 10}
        "intro-cs-lab_cos-126": {"count": 10, "average_minutes_per_request": 10}
        "intro-cs-lab_cos-217": {"count": 0, "average_minutes_per_request": 0}
        "intro-cs-lab_cos-226": {"count": 0, "average_minutes_per_request": 0}
    }
    """
    result = get_requests(netid)

    attendence = {
        "overall": {
            "count": result["count"],
            "average_minutes_per_request": 0,
        }
    }

    total_duration = 0
    for r in result["results"]:
        course = r["course"]
        if course not in attendance:
            time_accepted = datetime.strptime(
                r["time_accepted"], '%Y-%m-%dT%H:%M')
            time_closed = datetime.strptime(
                r["time_closed"], '%Y-%m-%dT%H:%M')
            duration = time_closed - time_accepted
            duration = divmod(duration.total_seconds(), 60)[0]
            total_duration += duration
            attendance[course] = {
                "count": 1,
                "average_minutes_per_request": duration,
            }
        else:
            time_accepted = datetime.strptime(
                r["time_accepted"], '%Y-%m-%dT%H:%M')
            time_closed = datetime.strptime(
                r["time_closed"], '%Y-%m-%dT%H:%M')
            duration = time_closed - time_accepted
            duration = divmod(duration.total_seconds(), 60)[0]
            total_duration += duration
            curr_av = attendance[course]["average_minutes_per_request"]
            curr_count = attendance[course]["count"]
            attendance[course]["average_minutes_per_request"] = (
                curr_av*curr_count + duration)/(curr_count + 1)

            attendance[course]["count"] += 1

    attendance["overall"]["average_minutes_per_request"] = total_duration / \
        attendance["overall"]["count"]

    return attendance
