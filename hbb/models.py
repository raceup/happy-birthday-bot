#!/usr/bin/env python
# coding: utf-8
import base64
import datetime

from hal.internet.email.templates import EmailTemplate
from hal.internet.email.utils import get_email_content
from hal.times.dates import Weekday, Day

from config import PRETTY_DATE_FORMAT, EMAIL_TEMPLATES, NOW, \
    PRETTY_BIRTHDAY_FORMAT
from utils import send_email


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
        text += get_email_content(EMAIL_TEMPLATES["cake"]["header"])
        text += "<br>Ti scrivo per ricordarti di portare almeno una torta "
        text += " la prossima volta in OZ <b>" + str(date_remainder) + \
                "</b>!<br>"

        return text


class CakeWarning(EmailTemplate):
    """ Email template to notify Race UP members to bring a slice of cake
    on weekly saturday meetings """

    def __init__(self, recipient, this_week_birthdays, content_file,
                 footer_file,
                 extra_args=None):
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
        self.this_week_birthdays = this_week_birthdays

    def get_birthdays_list(self):
        text = "In particolare "
        text += "\n<ul>"

        for birthday in self.this_week_birthdays:
            text += "<li>" + str(birthday) + "</li></br>"

        text += "</ul>"
        return text

    def get_email_header(self):
        """
        :return: str
            Email header
        """

        date_remainder = Weekday.get_next(Weekday.SATURDAY) \
            .strftime(PRETTY_DATE_FORMAT)
        text = "<h2>Ciao " + str(self.recipient).title() + "!</h2>"
        text += get_email_content(EMAIL_TEMPLATES["remind"]["header"])
        text += "<br>Ti scrivo per controllare le torte la prossima volta in " \
                "OZ <b>" + str(date_remainder) + "</b> </br></br>"
        text += self.get_birthdays_list() + "</br>"
        return text


class Birthday(object):
    """ Birthday data """

    def __init__(self, raw_dict):
        """
        :param raw_dict: {}
            Raw dict with values
        """

        self.raw_dict = raw_dict
        self.surname = str(self.raw_dict["Surname"])
        self.name = str(self.raw_dict["Name"])
        self.day = int(self.raw_dict["Day"])
        self.month = int(self.raw_dict["Month"])
        self.birthday = datetime.datetime(NOW.year, self.month, self.day)
        self.email = str(self.raw_dict["Email"])

    def __str__(self):
        return self.name + " " + self.surname + " compie gli anni " + \
               self.birthday.strftime(PRETTY_BIRTHDAY_FORMAT)

    def get_summary(self):
        return str(self.birthday.date().strftime(PRETTY_BIRTHDAY_FORMAT)) + \
               " >> " + self.name + " " + self.surname

    def is_this_week(self):
        """Checks if birthday happens this week

        :return: True iff birthday happens this week
        """

        return Day(self.birthday).is_in_this_week()

    def send_msg(self):
        """Sends message about cake remainder
        """

        send_email(self.get_cake_msg())

    def send_remainder_msg(self, this_week_birthdays):
        """Sends message about reminding cakes
        """

        send_email(self.get_remainder_msg(this_week_birthdays))

    def get_cake_msg(self):
        """
        :return: MIMEText
            Personalized message to notify of birthday
        """

        name_surname = self.name.strip()
        name_surname = name_surname.title()
        email_template = CakeRemainder(
            name_surname,
            EMAIL_TEMPLATES["cake"]["content"],
            EMAIL_TEMPLATES["cake"]["footer"]
        )

        message = email_template.get_mime_message()
        message["to"] = self.email

        return {
            "raw": base64.urlsafe_b64encode(message.as_bytes()).decode()
        }

    def get_remainder_msg(self, this_week_birthdays):
        """
        :return: MIMEText
            Personalized message to notify of cakes
        """

        name_surname = self.name.strip()
        name_surname = name_surname.title()
        email_template = CakeWarning(
            name_surname,
            this_week_birthdays,
            EMAIL_TEMPLATES["remind"]["content"],
            EMAIL_TEMPLATES["remind"]["footer"]
        )

        message = email_template.get_mime_message()
        message["to"] = self.email

        return {
            "raw": base64.urlsafe_b64encode(message.as_bytes()).decode()
        }


def get_this_week_list(birthdays):
    """Extracts birthdays that are this week

    :param birthdays: generator of birthdays
    :return: generator of birthdays happening this week
    """

    for b in birthdays:
        birthday = Birthday(b)  # parse raw csv data
        if birthday.is_this_week():
            yield birthday
