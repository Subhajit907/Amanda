import requests
import json
import csv
import os
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

# Config
headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

LOG_FILE = "output/test_emails.csv"
os.makedirs("output", exist_ok=True)

def fetch_new_web_submissions():
    query = """
    query ($board_id: [ID!]) {
      boards(ids: $board_id) {
        groups {
          id
          title
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

    groups = data["data"]["boards"][0]["groups"]
    new_web_group = next((g for g in groups if g["title"] == "New Web Submissions"), None)

    if not new_web_group:
        raise Exception("❌ 'New Web Submissions' group not found.")

    return new_web_group["items"]

def extract_value(column_values, target_id):
    for col in column_values:
        if col["id"] == target_id:
            return col.get("text", "")
    return ""

def log_email(to_email, first_name, subject, body):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["To Email", "Client First Name", "Subject", "Body"])
        writer.writerow([to_email, first_name, subject, body])

def main():
    try:
        items = fetch_new_web_submissions()
        for item in items:
            column_values = item["column_values"]
            first_name = extract_value(column_values, "text6")      # First Name
            to_email = extract_value(column_values, "email")        # Email

            if to_email and first_name:
                subject = "Thanks for your submission!"
                body = f"""Hi {first_name},

Thanks for reaching out to us! We're excited to learn more about your event and will get back to you shortly.

If you have any immediate questions, feel free to reply to this email.

Best,
Your Events Team"""

                log_email(to_email, first_name, subject, body)
                print(f"📄 Logged email to {to_email}")
            else:
                print(f"⚠️ Missing info for: {item['name']}")

    except requests.exceptions.RequestException as e:
        print(f"🚨 Network/API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
