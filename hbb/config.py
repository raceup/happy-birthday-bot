#!/usr/bin/env python
# coding: utf-8


import datetime
import locale
import os

from hal.internet.email import gmail

# folders
THIS_FOLDER = os.path.dirname(os.path.realpath(__file__))
DATA_FOLDER = os.path.join(os.path.dirname(THIS_FOLDER), "data")
OAUTH_FOLDER = os.path.join(THIS_FOLDER, ".user_credentials", "gmail")

# files
ADDRESSES_FILE = os.path.join(DATA_FOLDER, "addresses.csv")
LOCK_FILE = os.path.join(DATA_FOLDER, "config.json")

# dates
NOW = datetime.datetime.now()
TODAY = NOW.strftime('%A').lower()  # day
PRETTY_DATE_FORMAT = "%A %d %B %Y"
PRETTY_BIRTHDAY_FORMAT = "%A %d %B"

# app
APP_ORG = "Race UP"
APP_TITLE = "Happy Birthday Bot"
APP_NAME = "{} | {}".format(APP_ORG, APP_TITLE)

# email
EMAIL_DRIVER = gmail.GMailApiOAuth(
    "Race UP Viral",
    os.path.join(OAUTH_FOLDER, "client_secret.json"),
    os.path.join(OAUTH_FOLDER, "gmail.json")
).create_driver()
EMAIL_SENDER = "bot@raceup.it"
EMAIL_TEMPLATES = {
    "cake": {
        "header": os.path.join(DATA_FOLDER, "emails", "cake", "header.txt"),
        "content": os.path.join(DATA_FOLDER, "emails", "cake", "content.txt"),
        "footer": os.path.join(DATA_FOLDER, "emails", "cake", "footer.txt")
    },
    "remind": {
        "header": os.path.join(DATA_FOLDER, "emails", "remind", "header.txt"),
        "content": os.path.join(DATA_FOLDER, "emails", "remind", "content.txt"),
        "footer": os.path.join(DATA_FOLDER, "emails", "remind", "footer.txt")
    }
}
ADMIN_EMAIL = "stefano.fogarollo@raceup.it"

# locale
locale.setlocale(locale.LC_ALL, "it_IT.UTF-8")  # italian
