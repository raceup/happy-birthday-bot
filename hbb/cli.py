#!/usr/bin/env python
# coding: utf-8


import argparse

from hal.internet.utils import wait_until_internet
from hal.streams.notify.desktop import send_notification
from hal.times.cron import AppCronLock

from admin import desktop_notify
from bot import send_emails
from config import ADDRESSES_FILE, LOCK_FILE, APP_NAME


def create_and_parse_args():
    parser = argparse.ArgumentParser(
        usage="-a <ADDRESSES FILE> -l <LOCK FILE>\n"
              "-help for help and usage")
    parser.add_argument("-a", dest="addresses",
                        help="File containing addresses",
                        default=ADDRESSES_FILE,
                        required=False)
    parser.add_argument("-l", dest="lock",
                        help="File containing app lock and config",
                        default=LOCK_FILE,
                        required=False)
    parser.add_argument("-f", dest="force",
                        help="Force sending emails",
                        default=False,
                        required=False,
                        action='store_true')

    args = parser.parse_args()  # parse args

    return {
        "addresses": str(args.addresses),
        "lock": str(args.lock),
        "force": bool(args.force)
    }


def main():
    """
    :return: void
        Checks if today is right day to send email notifications, then sends them
    """

    args = create_and_parse_args()
    app_lock = AppCronLock(lock_file=args["lock"])
    can_proceed = app_lock.can_proceed() or args["force"]
    if can_proceed:
        print("Waiting for internet connection...")
        if wait_until_internet():
            print("...connected!")

            desktop_notify(
                send_emails(args["addresses"])
            )

            app_lock.write_lock()
        else:
            send_notification(
                APP_NAME,
                "Cannot connect to Internet >> Aborting"
            )
    else:
        send_notification(
            APP_NAME,
            "Already updated on " + str(app_lock.last_update)
        )


if __name__ == '__main__':
    main()
