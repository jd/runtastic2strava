#!/usr/bin/env python
import datetime
import json
import re

import requests
import six
import stravalib


with open("settings.json", "r") as f:
    settings = json.load(f)

STRAVA_UPLOAD = "upload@strava.com"


login = requests.post("https://www.runtastic.com/en/d/users/sign_in",
                      data={"user[email]": settings['runtastic_email'],
                            "user[password]": settings['runtastic_pass']})
resp = requests.get("https://www.runtastic.com/en/users/%s/sport-sessions"
                    % settings['runtastic_username'],
                    cookies=login.cookies)

activities = json.loads(re.search(r"index_data = ([^;]+);", resp.text).group(1))

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
    with file("archives/" + filename, "w+") as f:
        f.write(resp.text.encode("UTF-8"))
        f.seek(0)
        try:
            client.upload_activity(f, data_type="tcx")
        except stravalib.exc.ActivityUploadFailed as e:
            if 'duplicate' not in six.text_type(e):
                raise
    print("Sent activity %s from %s" % (activity_id, activity[1]))
