#!/usr/bin/env python
# coding: utf-8

import base64
from email.mime.text import MIMEText

from hal.streams.notify.desktop import send_notification

from config import APP_NAME, ADMIN_EMAIL
from utils import send_email


def send_summary(cakes, reminders):
    message = get_summary_message(cakes, reminders)
    message["to"] = ADMIN_EMAIL
    message = {
        "raw": base64.urlsafe_b64encode(message.as_bytes()).decode()
    }
    send_email(message)


def get_summary_message(cakes, reminders):
    total = len(cakes) + len(reminders)
    text = "Ciao foga,</br>sono il bot delle torte.</br>"

    text += "</br><h2>Totals:</h2><ul>"
    text += "<li># emails: " + str(total) + "</li></br>"
    text += "<li># cakes: " + str(len(cakes)) + "</li></br>"
    text += "<li># reminders: " + str(len(reminders)) + "</li></br>"
    text += "</ul>"

    text += "</br><h2>Cakes:</h2><ul>"
    for cake in cakes:
        text += "<li>" + cake["message"] + "</li>"
    text += "</ul>"

    text += "</br><h2>Reminders:</h2><ul>"
    for reminder in reminders:
        text += "<li>" + reminder["message"] + "</li>"
    text += "</ul>"

    message = MIMEText(
        "<html>" + text + "</html>", "html"
    )
    message["subject"] = APP_NAME
    return message


def desktop_notify(birthdays):
    """
    :param birthdays: [] of Birthday
        List of birthday to send notification to desktop
    :return: void
        Sends desktop notification about the birthdays
    """

    if birthdays:
        cakes = [b for b in birthdays if b["reason"] == "cake"]
        reminders = [b for b in birthdays if b["reason"] == "remind"]
        send_notification(APP_NAME, "# cakes: " + str(len(cakes)) + \
                          "\n# reminders: " + str(len(reminders)) + \
                          "\n\\nMore info sent by email to " + ADMIN_EMAIL)

        send_summary(cakes, reminders)
    else:
        send_notification(APP_NAME, "No cakes this week!")
