import requests
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

# Fetch item data from Monday.com
def fetch_items(board_id):
    query = """
    query ($board_id: [ID!]) {
      boards(ids: $board_id) {
        items_page {
          items {
            name
            column_values {
              id
              text
            }
          }
        }
      }
    }
    """
    variables = {"board_id": [board_id]}
    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    
    if "errors" in data:
        raise Exception(f"Items API Error: {data['errors']}")
    
    return data["data"]["boards"][0]["items_page"]["items"]


# Filter contacts with 'picnic' interest
def find_picnic_contacts(items):
    picnic_contacts = []

    for item in items:
        contact_info = {
            "first_name": "",
            "last_name": "",
            "email": "",
            "interests": ""
        }

        for col in item["column_values"]:
            if col["id"] == "text83":  # First name
                contact_info["first_name"] = col["text"]
            elif col["id"] == "text5":  # Last name
                contact_info["last_name"] = col["text"]
            elif col["id"] == "contact_email":  # Email
                contact_info["email"] = col["text"]
            elif col["id"] == "tags__1":  # Interests
                contact_info["interests"] = col["text"]

        if "picnic" in contact_info["interests"].lower():
            picnic_contacts.append(contact_info)

    return picnic_contacts


# Main execution
try:
    items = fetch_items(MONDAY_BOARD_ID)
    picnic_contacts = find_picnic_contacts(items)

    print("\n📋 Contacts interested in picnics:")
    if picnic_contacts:
        for contact in picnic_contacts:
            print(f"\n👤 {contact['first_name']} {contact['last_name']}")
            print(f"   ✉️ Email: {contact['email']}")
    else:
        print("No contacts found with picnic interest")

except requests.exceptions.RequestException as e:
    print(f"🚨 Network/API Error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
