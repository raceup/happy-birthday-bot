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

from hal.internet.email import gmail
from hal.internet.email.templates import EmailTemplate
from hal.internet.utils import wait_until_internet
from hal.streams.notify.desktop import send_notification
from hal.time import dates
from hal.time.cron import AppCronLock
from hal.time.dates import get_next_weekday, Weekday

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
EMAIL_HEADER_FILE = os.path.join(DATA_FOLDER, "email_header.txt")
EMAIL_CONTENT_FILE = os.path.join(DATA_FOLDER, "email_content.txt")
EMAIL_FOOTER_FILE = os.path.join(DATA_FOLDER, "email_footer.txt")


class CakeRemainder(EmailTemplate):
    """ Email template to notify Race Up members to bring a slice of cake
    on weekly saturday meetings """

    def __init__(self, recipient, content_file, footer_file, extra_args=None):
        """
        :param recipient: str
            Name and surname of email recipient
        :param content_file: str
            Path to file containing email actual content
        :param footer_file: str
            Path to file containing email footer (ending)
        :param extra_args: {}
            Details about next meeting date
        """

        EmailTemplate.__init__(
            self,
            recipient,
            "Race Up | Il bot delle torte",
            content_file,
            footer_file,
            extra_args=extra_args
        )

    def get_email_header(self):
        """
        :return: str
            Email header
        """

        date_remainder = get_next_weekday(Weekday.SATURDAY)
        text = "<h2>Ciao " + str(self.recipient).title() + "!</h2><br>"
        text += "<br>Ti scrivo per ricordarti di portare almeno una torta "
        text += " il prossimo sabato " + str(date_remainder) + " in OZ!<br>"
        return text


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
        self.birthday = datetime.datetime(NOW.year, self.month, self.day)
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

        name_surname = self.name.strip() + " " + self.surname.strip()
        name_surname = name_surname.title()
        email_template = CakeRemainder(
            name_surname,
            EMAIL_CONTENT_FILE,
            EMAIL_FOOTER_FILE
        )

        message = email_template.get_mime_message()
        message["to"] = self.email

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
                str(b.birthday.date().strftime("%a %b %d")) + " >> " + b.name
                + " " +
                b.surname
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
