#!/usr/bin/env python
# coding: utf-8

import csv

from config import ADDRESSES_FILE
from models import Birthday, get_this_week_list


def parse_data_file(in_file=ADDRESSES_FILE):
    """
    :return: [] of {}
        List of birthdays
    """

    reader = csv.DictReader(open(in_file, "r"))
    for row in reader:
        if row:
            yield row


def send_cake_remainder(birthdays):
    """Sends email remainder about cake to whoever turns

    :param birthdays: list of birthdays
    """

    this_week_birthdays = list(get_this_week_list(birthdays))
    for birthday in this_week_birthdays:
        birthday.send_msg()
        yield birthday


def send_birthday_remainder(birthdays):
    """Sends email remainder about people who turn to whoever does not turn

    :param birthdays: list of birthdays
    """

    this_week_birthdays = list(get_this_week_list(birthdays))
    if this_week_birthdays:  # just send emails if there is some birthday
        for b in birthdays:
            birthday = Birthday(b)  # parse raw csv data
            if not birthday.is_this_week():
                birthday.send_remainder_msg(this_week_birthdays)
                yield birthday


def send_emails(addresses):
    """
    :param addresses: str
        Path to file containing addresses
    :return: void
        Run bot
    """

    birthdays = list(parse_data_file(in_file=addresses))
    cakes_sent = list(send_cake_remainder(birthdays))
    reminders_sent = list(send_birthday_remainder(birthdays))

    # get summary
    cakes_sent = [
        {
            "reason": "cake",
            "message": cake.get_summary()
        } for cake in cakes_sent
    ]
    reminders_sent = [
        {
            "reason": "remind",
            "message": remind.get_summary()
        } for remind in reminders_sent
    ]

    return cakes_sent + reminders_sent
