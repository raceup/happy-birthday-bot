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

THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
DATA_FOLDER = os.path.join(THIS_FOLDER, "data")
EMAIL_HEADER_FILE = os.path.join(DATA_FOLDER, "email_header.txt")
EMAIL_CONTENT_FILE = os.path.join(DATA_FOLDER, "email_content.txt")
EMAIL_FOOTER_FILE = os.path.join(DATA_FOLDER, "email_footer.txt")


def get_file_as_email(file_path):
    """
    :param file_path: str
        Path to file with email text
    :return: str
        Email text (html formatted)
    """

    with open(file_path, "r") as in_file:
        text = str(in_file.read())
        return text.replace("\n", "<br>")


def get_email_header(name_surname):
    """
    :param name_surname: str
        Name and surname of email receiver
    :return: str
        Email header
    """

    text = "<h2>Ciao " + str(name_surname).title() + "!</h2><br>"
    return text + get_file_as_email(EMAIL_HEADER_FILE)


def get_email_content(next_meeting_date):
    """
    :param next_meeting_date: str
        Date of next meeting
    :return: str
        Email header
    """

    text = "<br>Ti scrivo per ricordarti di portare almeno una torta "
    text += " il prossimo sabato " + str(next_meeting_date) + " in OZ!<br>"
    return text + get_file_as_email(EMAIL_CONTENT_FILE)


def get_email_footer():
    """
    :param file_path: str
        Path to file with email text
    :return: str
        Email text (html formatted)
    """

    return get_file_as_email(EMAIL_FOOTER_FILE)
