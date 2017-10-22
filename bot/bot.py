# !/usr/bin/python
# coding: utf_8

# Copyright 2016-2017 Race UP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import base64
import csv
import datetime
import os
from email.mime.text import MIMEText

from emailutils import get_email_header, get_email_content, get_email_footer
from hal.internet import gmail
from hal.internet.utils import wait_until_internet
from hal.streams.notify.desktop import send_notification
from hal.time import dates
from hal.time.cron import AppCronLock

# script settings
THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
DATA_FOLDER = os.path.join(THIS_FOLDER, "data")
OAUTH_FOLDER = os.path.join(THIS_FOLDER, ".user_credentials", "gmail")
ADDRESSES_FILE = os.path.join(DATA_FOLDER, "addresses.csv")
LOCK_FILE = os.path.join(DATA_FOLDER, "config.json")

# date settings
NOW = datetime.datetime.now()
TODAY = NOW.strftime('%A').lower()  # day

# email settings
APP_NAME = "Race Up | Happy Birthday"
EMAIL_DRIVER = gmail.GMailApiOAuth(
    "Race Up Viral",
    os.path.join(OAUTH_FOLDER, "client_secret.json"),
    os.path.join(OAUTH_FOLDER, "gmail.json")
).create_driver()
EMAIL_SENDER = "bot@raceup.it"


class Birthday(object):
    """ Birthday data """

    def __init__(self, raw_dict):
        """
        :param raw_dict: {}
            Raw dict with values
        """

        object.__init__(self)
        self.raw_dict = raw_dict
        self.surname = str(self.raw_dict["Surname"])
        self.name = str(self.raw_dict["Name"])
        self.day = int(self.raw_dict["Day"])
        self.month = int(self.raw_dict["Month"])
        self.year = int(self.raw_dict["Year"])
        self.birthday = datetime.datetime(self.year, self.month, self.day)
        self.birthday_str = self.birthday.strftime("%A %d %B")
        self.email = str(self.raw_dict["Email"])

    def send_msg(self):
        """
        :return: bool
            Sends me a message if today is my birthday.
            Returns true iff sent message
        """

        if dates.is_in_this_week(self.birthday):
            try:
                send_email(self.get_msg())
                return True
            except Exception as e:
                print("Cannot send email because\n", str(e), "\n")
                return False

        return False

    def get_msg(self):
        """
        :return: MIMEText
            Personalized message to notify of birthday
        """

        name_surname = self.name + " " + self.surname
        next_meeting_date = dates.get_next_weekday(dates.Weekday.SATURDAY)
        next_meeting_date = str(next_meeting_date["day"]) + "/" + str(
            next_meeting_date["month"]) + "/" + str(
            next_meeting_date["year"])

        message = MIMEText(
            "<html>" +
            get_email_header(name_surname) +
            get_email_content(next_meeting_date) +
            get_email_footer() +
            "</html>", "html"
        )  # create message

        message["to"] = self.email  # email recipient
        message["subject"] = "Il bot delle torte | remainder"

        return {
            "raw": base64.urlsafe_b64encode(message.as_bytes()).decode()
        }


def parse_data_file(in_file=ADDRESSES_FILE):
    """
    :return: [] of {}
        List of birthdays
    """

    reader = csv.DictReader(open(in_file, "r"))
    for row in reader:
        if row:
            yield row


def desktop_notify(birthdays):
    """
    :param birthdays: [] of Birthday
        List of birthday to send notification to desktop
    :return: void
        Sends desktop notification about the birthdays
    """

    counter = 0
    if birthdays:
        for b in birthdays:
            send_notification(
                APP_NAME,
                str(b.birthday_str) + " >> " + b.name + " " + b.surname
                + " notified"
            )
            counter += 1
    else:
        send_notification(APP_NAME, "No birthdays this week!")
    send_notification(APP_NAME, "Sent " + str(counter) + " emails")


def send_email(msg):
    """
    :param msg: str
        Message to send to me
    :return: void
        Sends email to me with this message
    """

    gmail.send_email(
        EMAIL_SENDER,
        msg,
        EMAIL_DRIVER
    )


def send_emails():
    """
    :return: void
        Run bot
    """

    birthdays = parse_data_file()
    for b in birthdays:
        birthday = Birthday(b)  # parse raw csv data
        if birthday.send_msg():
            yield birthday


def main():
    """
    :return: void
        Checks if today is right day to send email notifications, then sends them
    """

    app_lock = AppCronLock(lock_file=LOCK_FILE)
    if app_lock.can_proceed():
        if wait_until_internet():
            desktop_notify(
                send_emails()
            )

            app_lock.write_lock()
        else:
            send_notification(
                APP_NAME,
                "Cannot connect to Internet >> Aborting"
            )
    else:
        send_notification(
            APP_NAME,
            "Already updated on " + str(app_lock.last_update)
        )


if __name__ == '__main__':
    main()
