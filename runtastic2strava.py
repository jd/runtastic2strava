#!/usr/bin/env python
import datetime
import json
import re
import sys

import requests
import six
import stravalib


with open("settings.json", "r") as f:
    settings = json.load(f)

STRAVA_UPLOAD = "upload@strava.com"


login = requests.post("https://www.runtastic.com/en/d/users/sign_in",
                      data={"user[email]": settings['runtastic_email'],
                            "user[password]": settings['runtastic_pass']})

if login.status_code // 100 != 2:
    print("Error logging in Runtastic, aborting")

resp = requests.get("https://www.runtastic.com/en/users/%s/sport-sessions"
                    % settings['runtastic_username'],
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
                 - datetime.timedelta(
                     days=settings.get('days_window', 3))).strftime("%Y-%m-%d")

client = stravalib.Client(
    access_token=settings.get("strava_access_token"))

# Only send the last N days of activities
for activity in filter(lambda a: a[1] >= last_sync_day, activities):
    activity_id = activity[0]
    resp = requests.get(
        "https://www.runtastic.com/en/users/%s/sport-sessions/%s.tcx"
        % (settings['runtastic_username'], activity_id),
        cookies=login.cookies)
    filename = "%s.tcx" % activity_id
    # Save the file locally, just in case.
    with open("archives/" + filename, "w+") as f:
        f.write(resp.text)
        f.seek(0)
        try:
            client.upload_activity(f, data_type="tcx")
        except stravalib.exc.ActivityUploadFailed as e:
            if not ('duplicate' in six.text_type(e)
                    or 'Unrecognized file type' in six.text_type(e)
                    or 'The file is empty' in six.text_type(e)):
                raise

    print("Sent activity %s from %s" % (activity_id, activity[1]))
