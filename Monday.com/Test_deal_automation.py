import requests
import json
import csv
import os
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

LOG_FILE = "email_log.csv"

def fetch_deals():
    query = """
    query ($board_id: [ID!]) {
      boards(ids: $board_id) {
        items_page {
          items {
            name
            column_values {
              id
              text
              value
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
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        raise Exception(f"API Error: {data['errors']}")

    return data["data"]["boards"][0]["items_page"]["items"]

def extract_value(column_values, target_id):
    for col in column_values:
        if col["id"] == target_id:
            return col.get("text", "")
    return ""

def get_rep_name(column_values):
    for col in column_values:
        if col["id"] == "person":  
            try:
                val = json.loads(col["value"] or "{}")
                if "personsAndTeams" in val and len(val["personsAndTeams"]) > 0:
                    return val["personsAndTeams"][0]["name"]
            except Exception:
                pass
    return "Sales Rep"

def log_email(rep_name, to_email, first_name, subject, body):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Rep", "To Email", "Client First Name", "Subject", "Body"])
        writer.writerow([rep_name, to_email, first_name, subject, body])

def main():
    try:
        items = fetch_deals()
        for item in items:
            column_values = item["column_values"]

            first_name = extract_value(column_values, "text83")  # First Name
            to_email = extract_value(column_values, "contact_email")  # Contact Email
            rep_name = get_rep_name(column_values)

            if to_email and first_name and rep_name:
                subject = "Thanks for contacting us!"
                body = f"""Hi {first_name},

Thank you for contacting us. I am reviewing your event details and will follow up with you soon.

If you have any other details about your event that you'd like to share, just reply here to reach me directly.

{rep_name}
 Amanda
"""
                log_email(rep_name, to_email, first_name, subject, body)
                print(f"📄 Logged email to {to_email} (Rep: {rep_name})")
            else:
                print(f"⚠️ Skipped deal due to missing data: {item['name']}")

    except requests.exceptions.RequestException as e:
        print(f"🚨 Network/API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
