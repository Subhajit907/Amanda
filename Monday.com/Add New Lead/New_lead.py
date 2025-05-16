import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

mutation = """
mutation ($board_id: ID!, $group_id: String!, $item_name: String!, $column_values: JSON!) {
  create_item(
    board_id: $board_id,
    group_id: $group_id,
    item_name: $item_name,
    column_values: $column_values
  ) {
    id
    name
  }
}
"""

# ✅ Replace with your actual data
item_name = "John Doe"
email_value = "john@example.com"
phone_value = "1234567890"  # Avoid dashes or symbols
about_event = "Wedding in September"
budget = "I don't know"

# ✅ Correct JSON structure for column values
column_values = {
    "email": {
        "email": email_value,
        "text": email_value
    },
    "phone": phone_value,
    "text41": about_event,  # "About Your Event"
    "text7": budget          # "Budget"
}

variables = {
    "board_id": str(MONDAY_BOARD_ID),    # Ensure this is a string
    "group_id": "topics",                # Confirmed group ID for 'New Web Submissions'
    "item_name": item_name,
    "column_values": json.dumps(column_values)  # Ensure valid JSON string
}

response = requests.post(
    "https://api.monday.com/v2",
    json={"query": mutation, "variables": variables},
    headers=headers
)

data = response.json()

if response.status_code != 200 or "errors" in data:
    print("❌ Failed to create lead:")
    print(json.dumps(data, indent=2))
else:
    item = data["data"]["create_item"]
    print(f"✅ Lead created successfully: {item['name']} (ID: {item['id']})")
