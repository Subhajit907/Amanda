import requests
import csv
import json
import os
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

GROUP_IDS = {
    "topics": "Active deals",
    "closed": "Booked",
    "new_group": "Not Booked",
    "new_group98809": "Not Qualified",
    "new_group__1": "Small - Sent Back to Brad"
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

# Step 2: Fetch items
items_query = {
    "query": f"""
    {{
      boards(ids: {MONDAY_BOARD_ID}) {{
        items_page(limit: 500) {{
          items {{
            id
            name
            group {{ id }}
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
    print(f"✅ Total items returned: {len(items)}")
    print(json.dumps(items[:2], indent=2))  # Debug: show first 2 items
    
    relevant_items = [item for item in items if item["group"]["id"] in GROUP_IDS]
    print(f"✅ Filtered to {len(relevant_items)} items from target groups")

    if not relevant_items:
        print("⚠️ No relevant items found. Check group IDs or data.")
        exit()

    rows = []
    for item in relevant_items:
        row = {
            "Group": GROUP_IDS.get(item["group"]["id"], item["group"]["id"]),
            "Deal Name": item["name"]
        }
        for col in item["column_values"]:
            col_title = column_id_to_title.get(col["id"], col["id"])
            row[col_title] = col["text"]
        rows.append(row)

    all_columns = set()
    for row in rows:
        all_columns.update(row.keys())
    fieldnames = sorted(all_columns)

    os.makedirs("output", exist_ok=True)
    with open("output/monday_crm_export.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("✅ CSV exported to 'output/monday_crm_export.csv'")
else:
    print("❌ Failed to fetch items")
    print("Status code:", items_response.status_code)
    print("Response:", items_response.text)