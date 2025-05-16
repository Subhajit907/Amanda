import requests
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

# GraphQL query to fetch board data
query = """
query ($board_id: [ID!]) {
  boards(ids: $board_id) {
    id
    name
    groups {
      id
      title
    }
    items_page {
      items {
        id
        name
        group {
          id
        }
        column_values {
          id
          text
        }
      }
    }
  }
}
"""

# GraphQL mutation to delete an item
delete_mutation = """
mutation ($item_id: ID!) {
  delete_item(item_id: $item_id) {
    id
  }
}
"""

# Fetch data from Monday.com
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

    emails_seen = set()

    print("✅ Items fetched. Checking for duplicates in 'New Web Submissions':")

    for item in items:
        group_id = item["group"]["id"]
        group_title = groups.get(group_id)

        if group_title != "New Web Submissions":
            continue

        details = {col["id"]: col["text"] for col in item["column_values"]}
        email = details.get("email", "").strip().lower()

        # Skip items without an email
        if not email:
            continue

        if email in emails_seen:
            # Duplicate found — delete the item
            delete_response = requests.post(
                "https://api.monday.com/v2",
                json={"query": delete_mutation, "variables": {"item_id": item["id"]}},  # Pass ID as string
                headers=headers
            )
            delete_data = delete_response.json()
            if delete_response.status_code == 200 and "errors" not in delete_data:
                print(f"✅ Successfully removed the duplicate from CRM: {email}")
            else:
                print(f"❌ Failed to delete item with email: {email} — {delete_data}")
        else:
            emails_seen.add(email)
