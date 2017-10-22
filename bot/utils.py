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


import os
import socket
import subprocess
import time

from hal.internet import gmail

APP_NAME = "Race Up | Happy Birthday"
THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
OAUTH_FOLDER = os.path.join(THIS_FOLDER, ".user_credentials", "gmail")
EMAIL_DRIVER = gmail.GMailApiOAuth(
    "Race Up Viral",
    os.path.join(OAUTH_FOLDER, "client_secret.json"),
    os.path.join(OAUTH_FOLDER, "gmail.json")
).create_driver()


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


def send_email(sender, msg):
    """
    :param sender: str
        Sender of email
    :param msg: str
        Message to send to me
    :return: void
        Sends email to me with this message
    """

    gmail.send_email(
        sender,
        msg,
        EMAIL_DRIVER
    )


def is_internet_on(host="8.8.8.8", port=53, timeout=3):
    """
    :param host: str
        Google-public-dns-a.google.com
    :param port: int
        53/tcp
    :param timeout: int
        Seconds
    :return: bool
        True iff machine has internet connection
    """

    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except:
        return False


def wait_until_internet(time_between_attempts=3, max_attempts=10):
    """
    :param time_between_attempts: int
        Seconds between 2 consecutive attempts
    :param max_attempts: int
        Max number of attempts to try
    :return: bool
        True iff there is internet connection
    """

    counter = 0
    while not is_internet_on():
        time.sleep(time_between_attempts)  # wait until internet is on
        counter += 1

        if counter > max_attempts:
            return False

    return True
