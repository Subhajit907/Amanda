
import requests
import smtplib
from email.mime.text import MIMEText
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

# Constants
MONDAY_API_URL = "https://api.monday.com/v2"
HEADERS = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

# Step 1: Fetch deals
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
        MONDAY_API_URL,
        json={"query": query, "variables": variables},
        headers=HEADERS
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]["boards"][0]["items_page"]["items"]

# Step 2: Send personalized email
def send_email(from_email, to_email, rep_name, client_first_name):
    subject = "Thank you for contacting us"
    body = f"""Hi {client_first_name},

Thank you for contacting us. I am reviewing your event details and will follow up with you soon.

If you have any other details about your event that you'd like to share, just reply here to reach me directly.

{rep_name}
"""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP("localhost") as server:  # Replace with actual SMTP server if needed
            server.sendmail(from_email, [to_email], msg.as_string())
        print(f"✅ Email sent from {from_email} to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

# Step 3: Process deals and trigger emails
def process_deals():
    deals = fetch_deals()
    for deal in deals:
        deal_data = {col["id"]: col["text"] for col in deal["column_values"]}
        contact_email = deal_data.get("contact_email", "")
        client_first_name = deal_data.get("text83", "")  # First name column
        rep_name = deal_data.get("person", "")  # Assigned person column
        from_email = "virtualemployee1996@gmail.com"  # Placeholder

        if contact_email and rep_name:
            send_email(from_email, contact_email, rep_name, client_first_name)

if __name__ == "__main__":
    process_deals()
