import json
from collections import Counter
from datetime import datetime
import requests
import logging

# Configuration for logging and Teams webhook
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
teams_webhook_url = 'Your_Teams_Webhook_URL'  # Replace with your Microsoft Teams webhook URL

# Read data from the JSON file
with open('filtered_events.json', 'r') as file:
    data = json.load(file)

# Initialize counters for statistics
events_per_computer = Counter()
events_per_rule = Counter()
events_per_day = Counter()
event_hours = Counter()

# Process each event in the data
for event in data:
    pc_name, rule, timestamp = event
    date = datetime.fromisoformat(timestamp).date()
    hour = datetime.fromisoformat(timestamp).hour

    # Increment counters
    events_per_computer[pc_name] += 1
    events_per_rule[rule] += 1
    events_per_day[date] += 1
    event_hours[hour] += 1

# Prepare the report message
report_message = "**Weekly Report**\n\n"
report_message += "**Triggered Rules**:\n"
for rule, count in events_per_rule.most_common():
    report_message += f"- {rule}: {count}\n"

report_message += "\n**Events by Computer**:\n"
for computer, count in events_per_computer.most_common():
    report_message += f"- {computer}: {count}\n"

report_message += "\n**Event Frequency by Day**:\n"
for day, count in sorted(events_per_day.items(), key=lambda x: x[1], reverse=True):
    report_message += f"- {day}: {count} events\n"

report_message += "\n**Hourly Event Count**:\n"
for hour, count in sorted(event_hours.items(), key=lambda x: x[1], reverse=True):
    report_message += f"- {hour}:00 - {count} events\n"

# Format the report message for Teams and send
formatted_report = {
    "type": "message",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "type": "AdaptiveCard",
                "version": "1.0",
                "body": [
                    {"type": "TextBlock", "size": "Medium", "weight": "Bolder", "text": report_message}
                ]
            }
        }
    ]
}
try:
    response = requests.post(teams_webhook_url, json=formatted_report)
    response.raise_for_status()
    logging.info("Weekly report sent successfully to Teams.")
except requests.exceptions.RequestException as e:
    logging.error(f"Error sending weekly report to Teams: {e}")
