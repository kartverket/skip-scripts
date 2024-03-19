#!/usr/bin/python3
"""This script checks login activity on the system and warns on Slack if a new login is detected.
Version: 2024-03-07_01
Dependencies: subprocess and slack_sdk (install with: pip3 install slack_sdk)
Tested on python 3.10.12 and python 3.6.8 with slack_sdk v3.27.0.
Make a notifier_config.py file with the following content:
HOSTNAME = "your-hostname"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXX"
The WEBHOOK URL can be obtained at https://api.slack.com/apps/A06KXH9GGAJ/incoming-webhooks?
Suggested installation method: add the script to the crontab to run every minute.
Author: Ole-Magnus Sæther - ole-magnus.saether AT kartverket.no
"""
import subprocess
from slack_sdk.webhook import WebhookClient
from notifier_config import SLACK_WEBHOOK_URL
from notifier_config import HOSTNAME


def send_message_to_slack(text):
    """Sends a message to Slack using the Slack Webhook URL.
    This is accomplished with slack_sdk v3.27.0.
    """
    url = SLACK_WEBHOOK_URL
    webhook = WebhookClient(url)

    response = webhook.send(
        text=text,
        blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": text}}],
    )
    assert response.status_code == 200
    assert response.body == "ok"


def monitor_logins():
    """
    Monitors login activity by comparing the current login timestamp with the last recorded timestamp.
    The functions does this by executing the 'last' command and reading the output.
    """
    timestamp_file = "/tmp/notifier_last_timestamp.txt"
    username_file = "/tmp/notifier_last_username.txt"
    NOTIFICATION_TO_SEND = None

    # Execute the 'last' command
    result = subprocess.run(["last", "-n", "1"], stdout=subprocess.PIPE)

    # Decode the output from bytes to string
    output = result.stdout.decode()

    # Split the output into lines
    lines = output.split("\n")

    # Get the username from the first line
    current_username = lines[0].split()[0]

    # Get remote hostname/IP
    remote_host = lines[0].split()[2]

    # Get the timestamp from the first line
    current_timestamp = lines[0].split()[6]

    try:
        # Read the last username from the file
        with open(username_file, "r") as file:
            last_username = file.read().strip()
    except FileNotFoundError:
        # If the file does not exist, create it and write the current username
        with open(username_file, "w") as file:
            file.write(current_username)
        return

    try:
        # Read the last timestamp from the file
        with open(timestamp_file, "r") as file:
            last_timestamp = file.read().strip()
    except FileNotFoundError:
        # If the file does not exist, create it and write the current timestamp
        with open(timestamp_file, "w") as file:
            file.write(current_timestamp)
        return

    # Compare the current timestamp with the last timestamp, add to variable if different
    if current_timestamp != last_timestamp:
        NOTIFICATION_TO_SEND = (
            ":rotating_light: "
            + HOSTNAME
            + " :rotating_light:"
            + "\n New login detected: "
            + "*"
            + current_username
            + "*"
            + " at "
            + current_timestamp
            + " from "
            + remote_host
        )

    # Write the current username to the file
    with open(username_file, "w") as file:
        file.write(current_username)

    # Write the current timestamp to the file
    with open(timestamp_file, "w") as file:
        file.write(current_timestamp)
    
    return NOTIFICATION_TO_SEND

def main():
    NOTIFICATION_TO_SEND = monitor_logins()

    if NOTIFICATION_TO_SEND:
        send_message_to_slack(NOTIFICATION_TO_SEND)
        #print(NOTIFICATION_TO_SEND) # for console output

if __name__ == "__main__":
    main()


