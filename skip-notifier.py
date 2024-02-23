#!/usr/bin/python3
"""This script checks login activity on the system and warns on Slack if a new login is detected.
Dependencies: subprocess and slack_sdk (install with: pip3 install slack_sdk)
Tested on python 3.10.12 and python 3.6.8 with slack_sdk v3.27.0.
Make a notifier_config.py file with the following content:
HOSTNAME = "your-hostname"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXX"
The WEBHOOK URL can be obtained at https://api.slack.com/apps/A06KXH9GGAJ/incoming-webhooks?
"""
import subprocess
from slack_sdk.webhook import WebhookClient
from notifier_config import SLACK_WEBHOOK_URL
from notifier_config import HOSTNAME

def send_message_to_slack(text):
    url = SLACK_WEBHOOK_URL
    webhook = WebhookClient(url)

    response = webhook.send(
      text=text,
      blocks=[
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": text
          }
        }
      ]   
    )
    assert response.status_code == 200
    assert response.body == "ok"

def monitor_logins():
  """
  Monitors login activity by comparing the current login timestamp with the last recorded timestamp.
  If a new login is detected, it prints the username and timestamp of the login.
  """
  timestamp_file = '/tmp/notifier_last_timestamp.txt'
  username_file = '/tmp/notifier_last_username.txt'

  # Execute the 'last' command
  result = subprocess.run(['last', '-n', '1'], stdout=subprocess.PIPE)

  # Decode the output from bytes to string
  output = result.stdout.decode()

  # Split the output into lines
  lines = output.split('\n')

  # Get the username from the first line
  current_username = lines[0].split()[0]

  # Get the timestamp from the first line
  current_timestamp = lines[0].split()[6]
  #print(current_username + ' logged in at ' + current_timestamp)
  
  try:
    # Read the last username from the file
    with open(username_file, 'r') as file:
      last_username = file.read().strip()
  except FileNotFoundError:
    # If the file does not exist, create it and write the current username
    with open(username_file, 'w') as file:
      file.write(current_username)
    return
  
  try:
    # Read the last timestamp from the file
    with open(timestamp_file, 'r') as file:
      last_timestamp = file.read().strip()
  except FileNotFoundError:
    # If the file does not exist, create it and write the current username
    with open(timestamp_file, 'w') as file:
      file.write(current_timestamp)
    return

  # Compare the current timestamp with the last timestamp
  if current_timestamp == last_timestamp:
    #print('New login detected: ' + current_username + ' at ' + current_timestamp)
    global NOTIFICATION_TO_SEND
    NOTIFICATION_TO_SEND = ':alert: ' + HOSTNAME + ' :alert:' + '\n New login detected: ' + '*' + current_username + '*' + ' at ' + current_timestamp

    #print(NOTIFICATION_TO_SEND)
    
  # Write the current username to the file
  with open(username_file, 'w') as file:
    file.write(current_username)

  # Write the current timestamp to the file
  with open(timestamp_file, 'w') as file:
    file.write(current_timestamp)

monitor_logins()

if 'NOTIFICATION_TO_SEND' in globals():
  send_message_to_slack(NOTIFICATION_TO_SEND)
  #print(NOTIFICATION_TO_SEND)