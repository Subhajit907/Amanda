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
    items_page {
      items {
        id
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
    items = data["data"]["boards"][0]["items_page"]["items"]

for item in items:
    details = {col["id"]: col["text"] for col in item["column_values"]}

    print("\n🧾 Contact:")
    print(f"  ➤ Name: {item['name']}")
    print(f"  ➤ Email: {details.get('email')}")
    print(f"  ➤ Phone: {details.get('phone')}")
    print(f"  ➤ First Name: {details.get('text6')}")
    print(f"  ➤ Last Name: {details.get('name')}")
    print(f"  ➤ Website: {details.get('text4')}")
    print(f"  ➤ Type of Event: {details.get('text41')}")

