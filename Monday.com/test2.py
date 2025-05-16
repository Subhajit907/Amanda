import requests
import json
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

# Step 1: Fetch column definitions (id → title)
columns_query = {
    "query": f"""
    {{
      boards(ids: {MONDAY_BOARD_ID}) {{
        columns {{
          id
          title
        }}
      }}
    }}
    """
}

columns_response = requests.post("https://api.monday.com/v2", json=columns_query, headers=headers)

if columns_response.status_code == 200:
    columns_data = columns_response.json()["data"]["boards"][0]["columns"]
    column_id_to_title = {col["id"]: col["title"] for col in columns_data}
else:
    print("❌ Failed to fetch column definitions")
    print("Status code:", columns_response.status_code)
    print("Response:", columns_response.text)
    exit()

# Step 2: Fetch items from the board
items_query = {
    "query": f"""
    {{
      boards(ids: {MONDAY_BOARD_ID}) {{
        items_page(limit: 100) {{
          items {{
            id
            name
            group {{
              id
            }}
            column_values {{
              id
              text
            }}
          }}
        }}
      }}
    }}
    """
}

items_response = requests.post("https://api.monday.com/v2", json=items_query, headers=headers)

if items_response.status_code == 200:
    items = items_response.json()["data"]["boards"][0]["items_page"]["items"]
    active_deals = [item for item in items if item["group"]["id"] == "topics"]

    print(f"✅ Found {len(active_deals)} items in 'Active deals':\n")
    for item in active_deals:
        print(f"- Deal Name: {item['name']}")
        for col in item['column_values']:
            col_title = column_id_to_title.get(col['id'], col['id'])
            print(f"  {col_title}: {col['text']}")
        print()
else:
    print("❌ Failed to fetch items")
    print("Status code:", items_response.status_code)
    print("Response:", items_response.text)
