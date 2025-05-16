import requests
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

emails_seen = set()
unique_contacts = []

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

query = """
query ($board_id: [ID!]) {
  boards(ids: $board_id) {
    id
    name
    columns {
      id
      title
      type
    }
    groups {
      id
      title
    }
    items_page(limit: 500) {
      items {
        id
        name
        group {
          id
        }
        column_values {
          id
          type
          text
          value
        }
      }
    }
  }
}
"""

variables = {"board_id": [MONDAY_BOARD_ID]}

response = requests.post(
    "https://api.monday.com/v2",
    json={"query": query, "variables": variables},
    headers=headers
)

data = response.json()

if response.status_code != 200 or "errors" in data:
    print("❌ Error:", data)
else:
    board = data["data"]["boards"][0]
    items = board["items_page"]["items"]
    groups = {g["id"]: g["title"] for g in board["groups"]}
    column_definitions = {col['id']: col['title'] for col in board['columns']}

    print("✅ Items fetched. Showing unique contacts from 'New Web Submissions':")

    for item in items:
        group_id = item["group"]["id"]
        group_title = groups.get(group_id)

        if group_title != "New Web Submissions":
            continue

        # Extract email from column_values
        email = None
        for col in item["column_values"]:
            if col["type"] == "email" and col["text"]:
                email = col["text"].strip().lower()
                break

        if not email:
            continue  # Skip items without an email

        if email in emails_seen:
            continue  # Skip duplicates

        emails_seen.add(email)
        unique_contacts.append(item)

        # Print contact info
        print(f"\n🧾 Contact: {item['name']} (Email: {email})")
        print(f"Group: {group_title}")
        print("Fields:")
        for col in item['column_values']:
            col_id = col['id']
            col_title = column_definitions.get(col_id, col_id)
            print(f"    - {col_title} (ID: {col_id}, Type: {col['type']}): {col['text']}")
