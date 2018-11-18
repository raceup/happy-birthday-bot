#!/usr/bin/env python
# coding: utf-8

from hal.internet.email import gmail

from config import EMAIL_SENDER, EMAIL_DRIVER


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
