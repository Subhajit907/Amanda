import requests
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

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

    print("✅ Items fetched. Showing unique contacts from 'New Web Submissions':")

    for item in items:
        group_id = item["group"]["id"]
        group_title = groups.get(group_id)

        if group_title != "New Web Submissions":
            continue

        details = {col["id"]: col["text"] for col in item["column_values"]}

        email = details.get("email", "").strip().lower()

        # Skip if email is missing or already seen
        if not email or email in emails_seen:
            continue

        emails_seen.add(email)

        print("\n🧾 Contact:")
        print(f"Name: {item['name']}")
        print(f"Email: {email}")
        print(f"Phone: {details.get('phone')}")
        print(f"First Name: {details.get('text6')}")
        print(f"Last Name: {details.get('name')}")
        print(f"Website: {details.get('text4')}")
        print(f"Type of Event: {details.get('text41')}")
