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
import datetime
import os
import subprocess
from email.mime.text import MIMEText

from google import gauthenticator

DATA_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_FILE_PATH = os.path.join(DATA_FILE_PATH, "data.csv")
DEBUG = True
NOW = datetime.datetime.now()
APP_NAME = "Race Up | Happy Birthday"


def send_notification(app_name, message):
    """
    :param app_name: str
        Name of app to show
    :param message: str
        Details of app to show
    :return: void
        Shows notifications to screen
    """

    subprocess.call([
        "notify-send",
        str(app_name),
        str(message)
    ])


def app_notify(message):
    """
    :param message: str
        Message to display in notification
    :return: void
        Shows notifications to screen
    """

    send_notification(APP_NAME, message)


class Utils(object):
    @staticmethod
    def get_date_of_last_week_sunday():
        """
        :return: datetime
            Date of this week's saturday
        """

        t = datetime.timedelta(- NOW.weekday() - 1)  # time D to last sunday
        return NOW + t

    @staticmethod
    def get_date_of_this_week_sunday():
        """
        :return: datetime
            Date of this week's monday
        """

        t = datetime.timedelta(
            (13 - NOW.weekday()) % 7
        )  # time delta to this monday
        return NOW + t

    @staticmethod
    def get_date_of_next_meeting():
        """
        :return: {}
            Day, month and year of next team meeting
        """

        t = datetime.timedelta(
            (12 - NOW.weekday()) % 7
        )  # time delta to next meeting (saturday)
        next_meeting = NOW + t

        return {
            "day": next_meeting.day,
            "month": next_meeting.month,
            "year": next_meeting.year
        }


class HbDataParser(object):
    """ Parses birthdays data """

    @staticmethod
    def parse(in_file):
        """
        :param in_file: str
            Path to file to parse
        :return: [] of {}
            List of raw columns of csv file
        """

        out = []
        lines = open(in_file, "r").readlines()[1:]  # discard header
        for line in lines:
            line = line.strip()  # remove any ending \n
            out.append(
                HbDataParser.parse_csv_line(line)
            )
        return out

    @staticmethod
    def parse_csv_line(line, values_delimiter=","):
        """
        :param line: str
            CSV line
        :param values_delimiter: str
            Char delimiter between values
        :return: {}
            Dict representation of line
        """

        tokens = line.split(values_delimiter)
        return {
            "surname": tokens[0],
            "name": tokens[1],
            "day": tokens[2],
            "month": tokens[3],
            "year": tokens[4],
            "email": tokens[5]
        }


class Birthday(object):
    """ Birthdayer data """

    def __init__(self, raw_dict):
        """
        :param raw_dict: {}
            Raw dict with values
        """

        self.raw_dict = raw_dict
        self.surname = str(self.raw_dict["surname"])
        self.name = str(self.raw_dict["name"])
        self.day = int(self.raw_dict["day"])
        self.month = int(self.raw_dict["month"])
        self.year = int(self.raw_dict["year"])
        self.birthday = datetime.datetime(self.year, self.month, self.day)
        self.email = str(self.raw_dict["email"])

    def notify_me_in_case_of_birthday(self):
        """
        :return: bool
            Sends me a message if today is my birthday.
            Returns true iff sent message
        """

        if self._do_i_turn_today():
            if DEBUG:
                print(
                    "\tSending birthday message to " +
                    self.email +
                    " (turns today!)"
                )
            msg = self._get_birthday_msg()  # message to send
            self._send_me_msg(msg)
            return True
        elif self._do_i_turn_this_week():
            if DEBUG:
                print(
                    "\tSending birthday message to " +
                    self.email +
                    " (turns " + str(self.day) + "/" + str(self.month) + ")"
                )
            msg = self._get_week_msg()  # message to send
            self._send_me_msg(msg)
            return True

        return False  # message not sent

    def _do_i_turn_today(self):
        """
        :return: bool
            True iff object's birthday is today
        """

        return NOW.month == self.month and NOW.day == self.day

    def _do_i_turn_this_week(self):
        """
        :return: bool
            True iff I turn this week
        """

        last_week_sunday = Utils.get_date_of_last_week_sunday()
        last_week_sunday = datetime.datetime(last_week_sunday.year,
                                             last_week_sunday.month,
                                             last_week_sunday.day)

        this_year_birthday = datetime.datetime(
            NOW.year,
            self.birthday.month,
            self.birthday.day
        )

        this_week_sunday = Utils.get_date_of_this_week_sunday()
        this_week_sunday = datetime.datetime(
            this_week_sunday.year,
            this_week_sunday.month,
            this_week_sunday.day
        )

        return last_week_sunday <= this_year_birthday < this_week_sunday

    def _get_birthday_msg(self):
        """
        :return: MIMEText
            Personalized message to notify of birthday
        """

        user_name = self.name + " " + self.surname
        next_meeting_date = Utils.get_date_of_next_meeting()
        next_meeting_date = str(next_meeting_date["day"]) + "/" + str(
            next_meeting_date["month"]) + "/" + str(
            next_meeting_date["year"])

        message = MIMEText(
            "<html>" +
            "<h2>Ciao " + user_name + "!</h2>" +
            "<p>" +
            "Sono il bot di Race UP<br>" +
            "Ti scrivo per augurarti buon compleanno " + user_name + "!<br>" +
            "Ti scrivo anche per ricordarti di portare almeno una torta il prossimo sabato " + next_meeting_date + " in OZ!<br>" +
            "Mi raccomando! Non dimenticarti: Gigetto è stato istruito a prendere provvedimenti in caso di negligenza.<br>" +
            "Ricordati di portare torte in quantità sufficiente per sfamare l'intero team: chi verrà sgammato a non provvedere sufficientemente alla fame generale,<br>" +
            "verrà impalato nella pubblica piazza dell'OZ.<br>" +
            "Sperando di mangiare più di una fetta,<br>" +
            "<br>" +
            "<i>Il bot delle torte</i><br>" +
            "<br>" +
            "<i>Race UP team</i><br>" +
            "<a href=\"https://twitter.com/RaceUpTeam\">Twitter</a><br>" +
            "<a href=\"https://it.linkedin.com/grps/Race-Up-Team-3555234/about?\">Linkedin</a><br>" +
            "<a href=\"https://www.facebook.com/Race-UP-Team-Combustion-440618820789/\">Facebook CD</a><br>" +
            "<a href=\"https://www.facebook.com/Race-UP-Team-Electric-802147286569414/\"\">Facebook ED</a><br>" +
            "<a href=\"https://www.instagram.com/race_up_team/\">Instagram</a><br>" +
            "<a href=\"https://www.youtube.com/user/teamraceup\">Youtube</a><br>" +
            "<a href=\"https://github.com/raceup\">Github</a><br>" +
            "<a href=\"https://bitbucket.org/raceuped\">Bitbucket</a><br>" +
            "<a href=\"mailto:info@raceup.it\">Email</a>" +
            "</p>" +
            "</html>", "html"
        )  # create message

        message["to"] = self.email  # email recipient
        message["subject"] = "Happy Birthday!"

        return {
            "raw": base64.urlsafe_b64encode(message.as_bytes()).decode()
        }

    def _get_week_msg(self):
        """
        :return: MIMEText
            Personalized message to notify of birthday
        """

        user_name = self.name + " " + self.surname
        next_meeting_date = Utils.get_date_of_next_meeting()
        next_meeting_date = str(next_meeting_date["day"]) + "/" + str(
            next_meeting_date["month"]) + "/" + str(
            next_meeting_date["year"])

        message = MIMEText(
            "<html>" +
            "<h2>Ciao " + user_name + "!</h2>" +
            "<p>" +
            "Sono il bot di Race UP<br>" +
            "Qualcosa mi dice che compi gli anni in questa settimana, giusto?<br>" +
            "Ti scrivo anche per ricordarti di portare almeno una torta il prossimo sabato " + next_meeting_date + " in OZ!<br>" +
            "Mi raccomando! Non dimenticarti: Gigetto è stato istruito a prendere provvedimenti in caso di negligenza.<br>" +
            "Ricordati di portare torte in quantità sufficiente per sfamare l'intero team: chi verrà sgammato a non provvedere sufficientemente alla fame generale,<br>"
            "verrà impalato nella pubblica piazza dell'OZ.<br>" +
            "Sperando di mangiare più di una fetta,<br>" +
            "<br>" +
            "<i>Il bot delle torte</i><br>" +
            "<br>" +
            "<i>Race UP team</i><br>" +
            "<a href=\"https://twitter.com/RaceUpTeam\">Twitter</a><br>" +
            "<a href=\"https://it.linkedin.com/grps/Race-Up-Team-3555234/about?\">Linkedin</a><br>" +
            "<a href=\"https://www.facebook.com/Race-UP-Team-Combustion-440618820789/\">Facebook CD</a><br>" +
            "<a href=\"https://www.facebook.com/Race-UP-Team-Electric-802147286569414/\"\">Facebook ED</a><br>" +
            "<a href=\"https://www.instagram.com/race_up_team/\">Instagram</a><br>" +
            "<a href=\"https://www.youtube.com/user/teamraceup\">Youtube</a><br>" +
            "<a href=\"https://github.com/raceup\">Github</a><br>" +
            "<a href=\"https://bitbucket.org/raceuped\">Bitbucket</a><br>" +
            "<a href=\"mailto:info@raceup.it\">Email</a>" +
            "</p>" +
            "</html>", "html"
        )  # create message

        message["to"] = self.email  # email recipient
        message["subject"] = "Slice of cake: a reminder!"

        return {
            "raw": base64.urlsafe_b64encode(message.as_bytes()).decode()
        }

    @staticmethod
    def _send_me_msg(msg):
        """
        :param msg: str
            Message to send to me
        :return: void
            Sends email to me with this message
        """

        service = gauthenticator.create_gmail_driver()
        service.users().messages().send(
            userId="bot.raceup@gmail.com",
            body=msg
        ).execute()  # send message


def run():
    """
    :return: void
        Run bot
    """

    birthdays = HbDataParser.parse(DATA_FILE_PATH)
    for b in birthdays:
        birthday = Birthday(b)  # parse raw csv data
        if birthday.notify_me_in_case_of_birthday():
            yield birthday


def notify_birthdays(birthdays):
    """
    :param birthdays: [] of Birthday
        List of birthday to send notification to desktop
    :return: void
        Sends desktop notification about the birthdays
    """

    if birthdays:
        for b in birthdays:
            app_notify(
                str(b.birthday) + " >>> " + b.name + " " + b.surname
                + " notified"
            )
    else:
        app_notify("No birthdays this week!")


def main():
    """
    :return: void
        Checks if today is right day to send email notifications, then sends them
    """

    today_str = NOW.strftime('%A').lower()
    if "mon" in today_str:  # this is a monday
        birthdays = run()  # launch bot
        notify_birthdays(birthdays)
    else:
        app_notify("Today is not monday! No need to send any email!")


if __name__ == '__main__':
    main()
