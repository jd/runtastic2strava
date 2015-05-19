#!/usr/bin/env python
import datetime
from email import encoders
from email import utils
import json
import re
import smtplib

from lxml import html
import requests
import six
from six.moves import email_mime_base
from six.moves import email_mime_multipart


with open("settings.json", "r") as f:
    settings = json.load(f)

STRAVA_UPLOAD = "upload@strava.com"


login = requests.post("https://www.runtastic.com/en/d/users/sign_in",
                      data={"user[email]": settings['runtastic_email'],
                            "user[password]": settings['runtastic_pass']})
resp = requests.get("https://www.runtastic.com/en/users/%s/sport-sessions"
                    % settings['runtastic_username'],
                    cookies=login.cookies)

tree = html.fromstring(resp.text)
js = tree.xpath('//script')[17].text
activities = json.loads(re.search(r"index_data = ([^;]+);", js).group(1))

last_sync_day = (datetime.datetime.utcnow()
                 - datetime.timedelta(
                     days=settings.get('days_window', settings['sync_days']))).strftime("%Y-%m-%d")

s = smtplib.SMTP(settings['smtp_server'])

# Only send the last N days of activities
for activity in filter(lambda a: a[1] >= last_sync_day, activities):
    activity_id = activity[0]
    resp = requests.get(
        "https://www.runtastic.com/en/users/%s/sport-sessions/%s.tcx"
        % (settings['runtastic_username'], activity_id),
        cookies=login.cookies)
    msg = email_mime_multipart.MIMEMultipart()
    msg['From'] = settings['strava_user']
    msg['To'] = STRAVA_UPLOAD
    msg['Subject'] = six.text_type(activity_id)
    msg['Date'] = utils.formatdate()
    part = email_mime_base.MIMEBase("application", "octet-stream")
    filename = "%s.tcx" % activity_id
    # Save the file locally, just in case.
    with file("archives/" + filename, "w") as f:
        f.write(resp.text.encode("UTF-8"))

    part.set_payload(resp.text)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',
                    'attachment; filename="%s"'
                    % filename)
    msg.attach(part)
    s.sendmail(settings['strava_user'], [STRAVA_UPLOAD], msg.as_string())
    print("Sent activity %s from %s" % (activity_id, activity[1]))

s.quit()
