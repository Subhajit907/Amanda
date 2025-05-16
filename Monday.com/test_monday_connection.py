import requests
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

query = {
    "query": f"""
    {{
      boards(ids: {MONDAY_BOARD_ID}) {{
        id
        name
        groups {{
          id
          title
        }}
      }}
    }}
    """
}

response = requests.post("https://api.monday.com/v2", json=query, headers=headers)

if response.status_code == 200:
    data = response.json()
    board = data['data']['boards'][0]
    print(f"✅ Connected to board '{board['name']}' (ID: {board['id']})")
    print(f"📌 Groups on board:")
    for group in board['groups']:
        print(f"  - {group['title']} (ID: {group['id']})")
       
else:
    print("❌ Failed to connect")
    print("Status code:", response.status_code)
    print("Response:", response.text)
