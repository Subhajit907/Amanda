import requests
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

# ✅ Corrected GraphQL query
query = """
query ($board_id: [ID!]) {
  boards(ids: $board_id) {
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

variables = {
    "board_id": [MONDAY_BOARD_ID]
}

response = requests.post(
    "https://api.monday.com/v2",
    json={"query": query, "variables": variables},
    headers=headers
)

# ✅ Error check
data = response.json()
if response.status_code != 200 or "errors" in data:
    print(f"❌ Error fetching data: {data}")
    exit()

# ✅ Extract items
items = data["data"]["boards"][0]["items_page"]["items"]

print("✅ Items fetched. Showing filtered contacts:\n")

for item in items:
    name = item['name']
    contact_info = {
        "email": "",
        "phone": "",
        "first_name": "",
        "last_name": "",
        "website": "",
        "interests": "",
        "deals": ""
    }

    for col in item["column_values"]:
        if col["id"] == "contact_email":
            contact_info["email"] = col["text"]
        elif col["id"] == "contact_phone":
            contact_info["phone"] = col["text"]
        elif col["id"] == "text83":
            contact_info["first_name"] = col["text"]
        elif col["id"] == "text5":
            contact_info["last_name"] = col["text"]
        elif col["id"] == "extract_info_mkmtc0x":
            contact_info["website"] = col["text"]
        elif col["id"] == "tags__1":
            contact_info["interests"] = col["text"]
        elif col["id"] == "deals": 
            contact_info["deals"] = col["text"]


    if "#picnics" in contact_info["interests"]:
        print(f"\n🧾 Contact: {name}")
        print(f"  ➤ Email: {contact_info['email']}")
        print(f"  ➤ Phone: {contact_info['phone']}")
        print(f"  ➤ Name: {contact_info['first_name']} {contact_info['last_name']}")
        print(f"  ➤ Website: {contact_info['website']}")
        print(f"  ➤ Interests: {contact_info['interests']}")
        print(f"  💼 Deals: {contact_info['deals']}")  # ✅ Now this will show actual data
        
        
    print(f"\n🧾 Contact: {name}")
    print(f"  ➤ Email: {contact_info['email']}")
    print(f"  ➤ Phone: {contact_info['phone']}")
    print(f"  ➤ Name: {contact_info['first_name']} {contact_info['last_name']}")
    print(f"  ➤ Website: {contact_info['website']}")





