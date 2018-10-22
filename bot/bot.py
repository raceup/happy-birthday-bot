# !/usr/bin/python
# coding: utf_8


import argparse
import base64
import csv
import datetime
import locale
import os

from hal.internet.email import gmail
from hal.internet.email.templates import EmailTemplate
from hal.internet.email.utils import get_email_content
from hal.internet.utils import wait_until_internet
from hal.streams.notify.desktop import send_notification
from hal.times.cron import AppCronLock
from hal.times.dates import Day, Weekday

# script settings
THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
DATA_FOLDER = os.path.join(THIS_FOLDER, "data")
OAUTH_FOLDER = os.path.join(THIS_FOLDER, ".user_credentials", "gmail")
ADDRESSES_FILE = os.path.join(DATA_FOLDER, "addresses.csv")
LOCK_FILE = os.path.join(DATA_FOLDER, "config.json")

# date settings
NOW = datetime.datetime.now()
TODAY = NOW.strftime('%A').lower()  # day
PRETTY_DATE_FORMAT = "%A %d %B %Y"

# email settings
APP_NAME = "Race UP | Happy Birthday"
EMAIL_DRIVER = gmail.GMailApiOAuth(
    "Race UP Viral",
    os.path.join(OAUTH_FOLDER, "client_secret.json"),
    os.path.join(OAUTH_FOLDER, "gmail.json")
).create_driver()
EMAIL_SENDER = "bot@raceup.it"
EMAIL_HEADER_FILE = os.path.join(DATA_FOLDER, "email_header.txt")
EMAIL_CONTENT_FILE = os.path.join(DATA_FOLDER, "email_content.txt")
EMAIL_FOOTER_FILE = os.path.join(DATA_FOLDER, "email_footer.txt")


# setting locale to get days in native language
locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")  # italian


class CakeRemainder(EmailTemplate):
    """ Email template to notify Race UP members to bring a slice of cake
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
            "URGENTISSIMO: Il bot delle torte",
            content_file,
            footer_file,
            extra_args=extra_args
        )

    def get_email_header(self):
        """
        :return: str
            Email header
        """

        date_remainder = Weekday.get_next(Weekday.SATURDAY) \
            .strftime(PRETTY_DATE_FORMAT)
        text = "<h2>Ciao " + str(self.recipient).title() + "!</h2>"
        text += get_email_content(EMAIL_HEADER_FILE)
        text += "<br>Ti scrivo per ricordarti di portare almeno una torta "
        text += " la prossima volta in OZ <b>" + str(date_remainder) + \
                "</b>!<br>"

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

        is_birthday_due = Day(self.birthday).is_in_this_week()
        if is_birthday_due:
            send_email(self.get_msg())
            return True

        return False

    def get_msg(self):
        """
        :return: MIMEText
            Personalized message to notify of birthday
        """

        name_surname = self.name.strip()
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
                str(b.birthday.date().strftime(PRETTY_DATE_FORMAT)) +
                " >> " + b.name + " " + b.surname + " notified"
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


def send_emails(addresses):
    """
    :param addresses: str
        Path to file containing addresses
    :return: void
        Run bot
    """

    birthdays = parse_data_file(in_file=addresses)
    for b in birthdays:
        birthday = Birthday(b)  # parse raw csv data
        if birthday.send_msg():
            yield birthday


def create_and_parse_args():
    parser = argparse.ArgumentParser(
        usage="-a <ADDRESSES FILE> -l <LOCK FILE>\n"
              "-help for help and usage")
    parser.add_argument("-a", dest="addresses",
                        help="File containing addresses",
                        default=ADDRESSES_FILE,
                        required=False)
    parser.add_argument("-l", dest="lock",
                        help="File containing app lock and config",
                        default=LOCK_FILE,
                        required=False)
    parser.add_argument("-f", dest="force",
                        help="Force sending emails",
                        default=False,
                        required=False,
                        action='store_true')

    args = parser.parse_args()  # parse args

    return {
        "addresses": str(args.addresses),
        "lock": str(args.lock),
        "force": bool(args.force)
    }


def main():
    """
    :return: void
        Checks if today is right day to send email notifications, then sends them
    """

    args = create_and_parse_args()
    app_lock = AppCronLock(lock_file=args["lock"])
    can_proceed = app_lock.can_proceed() or args["force"]
    if can_proceed:
        print("Waiting for internet connection...")
        if wait_until_internet():
            print("...connected!")

            desktop_notify(
                send_emails(args["addresses"])
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
