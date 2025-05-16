from flask import Flask, jsonify
import requests
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

app = Flask(__name__)

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}


def fetch_items(board_id):
    query = """
    query ($board_id: [ID!]) {
      boards(ids: $board_id) {
        items_page {
          items {
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
    variables = {"board_id": [board_id]}
    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    data = response.json()
    
    if "errors" in data:
        raise Exception(f"Items API Error: {data['errors']}")
    
    return data["data"]["boards"][0]["items_page"]["items"]


def filter_picnic_contacts(items):
    contacts = []

    for item in items:
        contact = {
            "first_name": "",
            "last_name": "",
            "email": "",
            "interests": ""
        }

        for col in item["column_values"]:
            if col["id"] == "text83":  # First name
                contact["first_name"] = col["text"]
            elif col["id"] == "text5":  # Last name
                contact["last_name"] = col["text"]
            elif col["id"] == "contact_email":  # Email
                contact["email"] = col["text"]
            elif col["id"] == "interests":  # Interests
                contact["interests"] = col["text"]

        if "picnic" in contact["interests"].lower():
            contacts.append(contact)

    return contacts


@app.route("/get-picnic-contacts", methods=["GET"])
def get_picnic_contacts():
    try:
        items = fetch_items(MONDAY_BOARD_ID)
        picnic_contacts = filter_picnic_contacts(items)

        return jsonify({
            "success": True,
            "count": len(picnic_contacts),
            "contacts": picnic_contacts
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"Network/API error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
