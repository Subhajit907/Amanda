import requests
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

query = """
query ($board_id: [ID!]) {
  boards(ids: $board_id) {
    columns {
      id
      title
      type
    }
  }
}
"""

variables = {"board_id": [MONDAY_BOARD_ID]}

try:
    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    
    if "errors" in data:
        raise Exception(f"API Error: {data['errors']}")
    
    columns = data["data"]["boards"][0]["columns"]
    print("\n🧾 Board Columns:")
    for col in columns:
        print(f"• {col['title']} (type: {col['type']}) => ID: {col['id']}")

except requests.exceptions.RequestException as e:
    print(f"🚨 Network/API Error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
