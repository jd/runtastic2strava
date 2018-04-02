#!/usr/bin/env python
import datetime
import json
import os
import re
import sys

import requests
import stravalib


EMAIL = os.getenv("RUNTASTIC_EMAIL")
PASSWORD = os.getenv("RUNTASTIC_PASS")
USERNAME = os.getenv("RUNTASTIC_USERNAME")
DAYS_WINDOW = int(os.getenv("RUNTASTIC_DAYS_WINDOW", 3))
STRAVA_ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
STRAVA_UPLOAD = "upload@strava.com"


login = requests.post("https://www.runtastic.com/en/d/users/sign_in",
                      data={"user[email]": EMAIL,
                            "user[password]": PASSWORD})

if login.status_code // 100 != 2:
    print("Error logging in Runtastic, aborting")

resp = requests.get("https://www.runtastic.com/en/users/%s/sport-sessions"
                    % USERNAME,
                    cookies=login.cookies)

if resp.status_code // 100 != 2:
    print("Error doing Runtastic request, aborting")
    sys.exit(1)

match_data = re.search(r"index_data = ([^;]+);", resp.text)
if not match_data:
    print("Error looking for data, aborting")
    sys.exit(1)

activities = json.loads(match_data.group(1))

last_sync_day = (datetime.datetime.utcnow()
                 - datetime.timedelta(days=DAYS_WINDOW)).strftime("%Y-%m-%d")

client = stravalib.Client(access_token=STRAVA_ACCESS_TOKEN)

# Only send the last N days of activities
for activity in filter(lambda a: a[1] >= last_sync_day, activities):
    activity_id = activity[0]
    resp = requests.get(
        "https://www.runtastic.com/en/users/%s/sport-sessions/%s.tcx"
        % (USERNAME, activity_id),
        cookies=login.cookies)
    filename = "%s.tcx" % activity_id
    # Save the file locally, just in case.
    with open(filename, "w+") as f:
        f.write(resp.text)
        f.seek(0)
        try:
            client.upload_activity(f, data_type="tcx")
        except stravalib.exc.ActivityUploadFailed as e:
            if not ('duplicate' in str(e)
                    or 'Unrecognized file type' in str(e)
                    or 'The file is empty' in str(e)):
                raise

    print("Sent activity %s from %s" % (activity_id, activity[1]))
