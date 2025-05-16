import requests
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

GROUP_IDS = [
    "topics",            # Active deals
    "closed",            # Booked
    "new_group",         # Not Booked
    "new_group98809",    # Not Qualified
    "new_group__1"       # Small - Sent Back to Brad
]

def fetch_all_group_deals():
    query = {
        "query": f"""
        {{
          boards(ids: {MONDAY_BOARD_ID}) {{
            items_page(limit: 500) {{
              items {{
                id
                name
                group {{ id }}
                column_values {{ id text }}
              }}
            }}
          }}
        }}
        """
    }
    response = requests.post("https://api.monday.com/v2", json=query, headers=headers)
    if response.status_code == 200:
        items = response.json()["data"]["boards"][0]["items_page"]["items"]
        filtered = [item for item in items if item["group"]["id"] in GROUP_IDS]
        return filtered
    else:
        raise Exception(f"API Error: {response.status_code} {response.text}")
