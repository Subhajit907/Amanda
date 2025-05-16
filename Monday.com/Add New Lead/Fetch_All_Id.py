import requests
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

query = """
query ($board_id: [ID!]) {
  boards(ids: $board_id) {
    name
    groups {
      id
      title
    }
  }
}
"""

variables = {
    "board_id": [MONDAY_BOARD_ID]
}

response = requests.post(
    "https://api.monday.com/v2",
    json={"query": query, "variables": variables},
    headers=headers
)

data = response.json()

if response.status_code != 200 or "errors" in data:
    print("❌ Error fetching groups:", data)
else:
    groups = data["data"]["boards"][0]["groups"]
    print("✅ Available Groups:")
    for group in groups:
        print(f"- Title: {group['title']}, ID: {group['id']}")
