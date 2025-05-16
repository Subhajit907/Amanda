import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

# Function to find the item by email
def find_item_by_email(email):
    query = """
    query ($board_id: ID!) {
      boards(ids: [$board_id]) {
        items {
          id
          name
          column_values {
            id
            text
            title
          }
        }
      }
    }
    """
    
    variables = {
        "board_id": MONDAY_BOARD_ID,  # Use your board ID here
    }

    # Send the request to find the item
    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query, "variables": variables},
        headers=headers
    )

    data = response.json()

    if response.status_code != 200 or "errors" in data:
        print("❌ Failed to find item:")
        print(data)
        return None
    else:
        items = data["data"]["boards"][0]["items"]
        for item in items:
            # Check if the email matches the column value
            for column in item["column_values"]:
                if column["text"] == email:
                    print(f"✅ Found item with email {email}, item ID: {item['id']}")
                    return item["id"]
        print(f"❌ No item found with email {email}")
        return None

# Function to delete the lead
def delete_lead(item_id):
    mutation = """
    mutation ($item_id: ID!) {
        delete_item(item_id: $item_id) {
            id
        }
    }
    """

    variables = {
        "item_id": item_id
    }

    # Send the request to delete the item
    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": mutation, "variables": variables},
        headers=headers
    )

    data = response.json()

    if response.status_code != 200 or "errors" in data:
        print("❌ Failed to delete lead:")
        print(data)
    else:
        deleted_id = data["data"]["delete_item"]["id"]
        print(f"✅ Successfully deleted lead with ID: {deleted_id}")

# Main process to delete based on email
email_to_delete = "john@example.com"  # Replace with the email you used to create the lead

# Step 1: Find the item by email
item_id = find_item_by_email(email_to_delete)

# Step 2: If item is found, delete it
if item_id:
    delete_lead(item_id)
