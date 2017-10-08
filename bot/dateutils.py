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


import datetime

NOW = datetime.datetime.now()


def get_date_of_last_week_sunday():
    """
    :return: datetime
        Date of this week's saturday
    """

    t = datetime.timedelta(- NOW.weekday() - 1)  # time D to last sunday
    return NOW + t


def get_date_of_this_week_sunday():
    """
    :return: datetime
        Date of this week's monday
    """

    t = datetime.timedelta(
        (13 - NOW.weekday()) % 7
    )  # time delta to this monday
    return NOW + t


def get_date_of_next_meeting():
    """
    :return: {}
        Day, month and year of next team meeting
    """

    t = datetime.timedelta(
        (12 - NOW.weekday()) % 7
    )  # time delta to next meeting (saturday)
    next_meeting = NOW + t

    return {
        "day": next_meeting.day,
        "month": next_meeting.month,
        "year": next_meeting.year
    }
