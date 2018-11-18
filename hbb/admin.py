#!/usr/bin/env python
# coding: utf-8

from hal.streams.notify.desktop import send_notification

from config import APP_NAME, ADMIN_EMAIL


def send_summary(cakes, reminders):
    pass  # todo


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
