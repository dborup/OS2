import requests
from datetime import datetime, timedelta

# Configuration Variables
api_token = 'Your_API_Token' # API token for authorization with the event system
teams_webhook_url = 'Your_Teams_Webhook_URL' # Microsoft Teams webhook URL for notifications
monitoring_rule = 'Your_Monitor_Rule'  # Monitoring rule to filter events

# Function to reformat the timestamp
def reformat_timestamp(timestamp_str):
    original_format = '%Y-%m-%dT%H:%M:%S.%f'
    try:
        datetime_obj = datetime.strptime(timestamp_str, original_format)
    except ValueError:
        return timestamp_str
    new_format = '%H:%M:%S %d-%m-%Y'
    return datetime_obj.strftime(new_format)

# Date calculations for the API request
current_date = datetime.now()
seven_days_ago = current_date - timedelta(days=7)
formatted_seven_days_ago = seven_days_ago.strftime('%Y-%m-%d')

# API endpoint and headers setup for system events
events_url = 'https://os2borgerpc-admin.magenta.dk/api/system/events'
headers = {'accept': 'application/json', 'Authorization': f'Bearer {api_token}'}
params = {
    'from_date': formatted_seven_days_ago,
    'to_date': current_date.strftime('%Y-%m-%d'),
    'status': 'NEW',
    'limit': 100,
    'offset': 0
}

# Fetching system events
events_response = requests.get(events_url, headers=headers, params=params)
events_data = events_response.json()

# Filtering events based on the monitoring rule
filtered_items = [item for item in events_data['items'] if item['monitoring_rule'] == monitoring_rule]

# Proceed only if there are filtered items
if filtered_items:
    # Extracting pc_name from filtered events
    pc_names = [item['pc_name'] for item in filtered_items]

    # API endpoint for computers information
    computers_url = 'https://os2borgerpc-admin.magenta.dk/api/system/computers'

    # Fetching computer details
    computers_response = requests.get(computers_url, headers=headers)
    computers_data = computers_response.json()

    # Mapping computer names to their details
    computers_dict = {computer['name']: computer for computer in computers_data}

    # Matching each pc_name with corresponding computer details
    matched_computers = [computers_dict.get(pc_name) for pc_name in pc_names]

    # Function to create an AdaptiveCard for Teams
    def format_adaptive_card(computers):
        current_date_str = datetime.now().strftime('%d-%m-%Y')  # Get current date in DD-MM-YYYY format
        report_title = f"System Event Report - {current_date_str}"

        card = {
            "type": "AdaptiveCard",
            "version": "1.0",
            "body": [{"type": "TextBlock", "size": "Medium", "weight": "Bolder", "text": report_title}]
        }

        for computer in computers:
            if computer:
                last_seen_formatted = reformat_timestamp(computer['last_seen'])
                facts = [
                    {"title": "Name", "value": computer['name']},
                    {"title": "Location", "value": computer['location']},
                    {"title": "Last Seen", "value": last_seen_formatted},
                    {"title": "IP", "value": computer['ip_addresses']}
                ]
                card["body"].append({"type": "FactSet", "facts": facts})

        return {"type": "message", "attachments": [{"contentType": "application/vnd.microsoft.card.adaptive", "content": card}]}

    # Format the message for Teams
    formatted_message = format_adaptive_card(matched_computers)

    # Sending the message to the Teams webhook
    response = requests.post(teams_webhook_url, json=formatted_message)

    # Checking and printing the response status
    if response.status_code == 200:
        print("Message sent successfully to Teams.")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
else:
    print("No relevant events to report.")
