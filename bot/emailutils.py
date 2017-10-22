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

from hal.internet.email.templates import EmailTemplate

THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
DATA_FOLDER = os.path.join(THIS_FOLDER, "data")
EMAIL_HEADER_FILE = os.path.join(DATA_FOLDER, "email_header.txt")
EMAIL_CONTENT_FILE = os.path.join(DATA_FOLDER, "email_content.txt")
EMAIL_FOOTER_FILE = os.path.join(DATA_FOLDER, "email_footer.txt")


class CakeRemainder(EmailTemplate):
    """ Email template to notify Race Up members to bring a slice of cake
    on weekly saturday meetings """

    def __init__(self, recipient, content_file, extra_args=None):
        """
        :param recipient: str
            Name and surname of email recipient
        :param content_file: str
            Path to file containing email actual content
        :param extra_args: {}
            Details about next meeting date
        """

        EmailTemplate.__init__(
            self,
            recipient,
            "Race Up | Il bot delle torte",
            content_file,
            EMAIL_FOOTER_FILE,
            extra_args=extra_args
        )

    def get_email_header(self):
        """
        :return: str
            Email header
        """

        date_remainder = get_next_weekday(Weekday.SATURDAY)
        text = "<h2>Ciao " + str(self.recipient).title() + "!</h2><br>"
        text += "<br>Ti scrivo per ricordarti di portare almeno una torta "
        text += " il prossimo sabato " + str(date_remainder) + " in OZ!<br>"
        return text
