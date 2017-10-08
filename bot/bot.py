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
import json
import os
from email.mime.text import MIMEText

from dateutils import NOW, get_date_of_last_week_sunday, \
    get_date_of_this_week_sunday, get_date_of_next_meeting
from emailutils import get_email_header, get_email_content, get_email_footer
from utils import app_notify, send_email

THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
DATA_FOLDER = os.path.join(THIS_FOLDER, "data")
ADDRESSES_FILE = os.path.join(DATA_FOLDER, "addresses.csv")
LOCK_FILE = os.path.join(DATA_FOLDER, "config.json")
EMAIL_SENDER = "bot@raceup.it"
TODAY = NOW.strftime('%A').lower()  # day


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

        if self.do_i_turn_this_week():
            send_email(
                EMAIL_SENDER,
                self.get_msg()
            )
            return True

        return False

    def do_i_turn_this_week(self):
        """
        :return: bool
            True iff I turn this week
        """

        last_week_sunday = get_date_of_last_week_sunday()
        last_week_sunday = datetime.datetime(
            last_week_sunday.year,
            last_week_sunday.month,
            last_week_sunday.day
        )  # avoid dealing with 24:00

        this_year_birthday = datetime.datetime(
            NOW.year,
            self.birthday.month,
            self.birthday.day
        )

        this_week_sunday = get_date_of_this_week_sunday()
        this_week_sunday = datetime.datetime(
            this_week_sunday.year,
            this_week_sunday.month,
            this_week_sunday.day
        )  # avoid dealing with 24:00

        return last_week_sunday < this_year_birthday <= this_week_sunday

    def get_msg(self):
        """
        :return: MIMEText
            Personalized message to notify of birthday
        """

        name_surname = self.name + " " + self.surname
        next_meeting_date = get_date_of_next_meeting()
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


class AppLock(object):
    """ Checks if app can proceed; generates lock """

    DATETIME_FORMAT = "%Y-%m-%d %H:%S:%M"

    def __init__(self, lock_file=LOCK_FILE):
        """
        :param lock_file: str
            Path to lock file
        """

        object.__init__(self)
        self.lock_file = lock_file
        self.update_interval = 7
        self.last_update = datetime.datetime.fromtimestamp(0)
        self.data = None
        self.parse_lock()

    def set_update_interval(self, days=7):
        """
        :param days: int
            Days between 2 consecutive app updates
        :return: void
            Sets app interval update
        """

        self.update_interval = days

    def can_proceed(self):
        """
        :return: bool
            True iff app is not locked and time since last update < app
            update interval
        """

        return NOW >= self.last_update + datetime.timedelta(
            days=self.update_interval)

    def parse_lock(self):
        """
        :return: {}
            Details about last update
        """

        try:
            with open(self.lock_file, "r") as reader:
                data = json.loads(reader.read())
                self.last_update = datetime.datetime.strptime(
                    data["last_update"],
                    AppLock.DATETIME_FORMAT
                )
        except:  # malformed lock file
            self.write_lock(last_update=datetime.datetime.fromtimestamp(0))
            self.parse_lock()

    def write_lock(self, last_update=NOW):
        """
        :return: void
            Writes lock file
        """

        data = {
            "last_update": last_update.strftime(AppLock.DATETIME_FORMAT)
        }

        with open(self.lock_file, "w") as writer:
            json.dump(data, writer)


def parse_data_file(in_file=ADDRESSES_FILE):
    """
    :return: [] of {}
        List of birthdays
    """

    reader = csv.DictReader(open(in_file, "r"))
    for row in reader:
        if row:
            yield row


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


def send_desktop_notifications(birthdays):
    """
    :param birthdays: [] of Birthday
        List of birthday to send notification to desktop
    :return: void
        Sends desktop notification about the birthdays
    """

    counter = 0
    if birthdays:
        for b in birthdays:
            app_notify(
                str(b.birthday_str) + " >> " + b.name + " " + b.surname
                + " notified"
            )
            counter += 1
    else:
        app_notify("No birthdays this week!")
    app_notify(
        "Sent " + str(counter) + " emails"
    )


def main():
    """
    :return: void
        Checks if today is right day to send email notifications, then sends them
    """

    app_lock = AppLock()
    if app_lock.can_proceed():
        send_desktop_notifications(
            send_emails()
        )

        app_lock.write_lock()
    else:
        app_notify("Already updated on " + str(app_lock.last_update))


if __name__ == '__main__':
    main()
