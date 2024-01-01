#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration Variables
api_token = 'Your_API_Token' # API token for authorization with the event system
teams_webhook_url = 'Your_Teams_Webhook_URL' # Microsoft Teams webhook URL for notifications
monitoring_rules = ['Nyt Keyboard Detect', 'Sudo', 'Detekter låst/udløbet bruger']  # Monitoring rules
days_back = 7  # Number of days to look back for events

# Function to reformat timestamps
def reformat_timestamp(timestamp_str):
    formats = ['%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S']
    for fmt in formats:
        try:
            datetime_obj = datetime.strptime(timestamp_str, fmt)
            new_format = '%H:%M:%S %d-%m-%Y'
            return datetime_obj.strftime(new_format)
        except ValueError:
            continue
    logging.error(f"Timestamp format error for {timestamp_str}")
    return timestamp_str

# Date calculations for API requests
current_date = datetime.now()
days_ago = current_date - timedelta(days=days_back)
formatted_days_ago = days_ago.strftime('%Y-%m-%d')

# API endpoint and headers setup for system events
events_url = 'https://os2borgerpc-admin.magenta.dk/api/system/events'
headers = {'accept': 'application/json', 'Authorization': f'Bearer {api_token}'}
params = {
    'from_date': formatted_days_ago,
    'to_date': current_date.strftime('%Y-%m-%d'),
    'status': 'NEW',
    'limit': 1000,
    'offset': 0
}

# Fetching system events
try:
    events_response = requests.get(events_url, headers=headers, params=params)
    events_response.raise_for_status()
    events_data = events_response.json()
    logging.info("Successfully fetched system events.")
except requests.exceptions.HTTPError as errh:
    logging.error(f"HTTP Error: {errh}")
except requests.exceptions.ConnectionError as errc:
    logging.error(f"Error Connecting: {errc}")
except requests.exceptions.Timeout as errt:
    logging.error(f"Timeout Error: {errt}")
except requests.exceptions.RequestException as err:
    logging.error(f"Error: {err}")

# Check for 'items' in the response and filter them
if 'items' in events_data:
    filtered_items = [(item['pc_name'], item['monitoring_rule'], item['occurred_time']) for item in events_data['items'] if item['monitoring_rule'] in monitoring_rules]
else:
    logging.warning("The 'items' key was not found in the API response.")
    filtered_items = []

# Fetch computer details if there are filtered items
if filtered_items:
    computers_url = 'https://os2borgerpc-admin.magenta.dk/api/system/computers'
    try:
        computers_response = requests.get(computers_url, headers=headers)
        computers_response.raise_for_status()
        computers_data = computers_response.json()
        logging.info("Successfully fetched computer details.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching computer details: {e}")
        computers_data = []

    computers_dict = {computer['name']: computer for computer in computers_data}

    # Function to format adaptive cards for Teams
    def format_adaptive_card(computer, rule, occurred_time):
        occurred_time_formatted = reformat_timestamp(occurred_time)
        report_title = f"{rule} - {occurred_time_formatted}"

        card = {
            "type": "AdaptiveCard",
            "version": "1.0",
            "body": [{"type": "TextBlock", "size": "Medium", "weight": "Bolder", "text": report_title}]
        }

        if computer:
            last_seen_formatted = reformat_timestamp(computer.get('last_seen', ''))

            ip_address = computer.get('ip_addresses', '')
            if isinstance(ip_address, list):
                ip_address = ', '.join(ip_address)

            facts = [
                {"title": "Name", "value": computer['name']},
                {"title": "Location", "value": computer['location']},
                {"title": "Last Seen", "value": last_seen_formatted},
                {"title": "IP", "value": ip_address}
            ]
            card["body"].append({"type": "FactSet", "facts": facts})

        return {"type": "message", "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}]}

    # Sending notifications to Teams
    for pc_name, rule, occurred_time in filtered_items:
        computer = computers_dict.get(pc_name)
        if computer:
            formatted_message = format_adaptive_card(computer, rule, occurred_time)
            try:
                response = requests.post(teams_webhook_url, json=formatted_message)
                response.raise_for_status()
                logging.info(f"Message sent successfully to Teams for {pc_name}.")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error sending message to Teams for {pc_name}: {e}")
else:
    logging.info("No relevant events to report.")
