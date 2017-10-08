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


import subprocess

from google import gauthenticator

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


def send_email(sender, msg):
    """
    :param sender: str
        Sender of email
    :param msg: str
        Message to send to me
    :return: void
        Sends email to me with this message
    """

    service = gauthenticator.create_gmail_driver()
    service.users().messages().send(
        userId=sender,
        body=msg
    ).execute()  # send message
