import requests
import smtplib
from email.message import EmailMessage
from config import MONDAY_API_KEY, MONDAY_BOARD_ID, EMAIL_SENDER, EMAIL_PASSWORD

# Setup headers
headers = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

# Monday.com GraphQL Query
query = """
query ($board_id: [ID!]) {
  boards(ids: $board_id) {
    id
    groups {
      id
      title
    }
    items_page(limit: 500) {
      items {
        id
        name
        group {
          id
        }
        column_values {
          id
          text
        }
      }
    }
  }
}
"""

variables = {"board_id": [MONDAY_BOARD_ID]}

# Fetch data
response = requests.post(
    "https://api.monday.com/v2",
    json={"query": query, "variables": variables},
    headers=headers
)
data = response.json()

if response.status_code != 200 or "errors" in data:
    print("❌ Error fetching data:", data)
    exit()

# Track seen emails to avoid duplicates
emails_sent = set()
board = data["data"]["boards"][0]
items = board["items_page"]["items"]
groups = {g["id"]: g["title"] for g in board["groups"]}

# Email sender setup
def send_email(to_email, name):
    msg = EmailMessage()
    msg["Subject"] = "Thanks for your submission!"
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email

    msg.set_content(f"""
Hi {name},

Thank you for reaching out. We’ve received your request and will get back to you shortly.

Best regards,
Your Company Team
    """)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)

# Loop through leads
for item in items:
    group_id = item["group"]["id"]
    group_title = groups.get(group_id)

    if group_title != "New Web Submissions":
        continue

    details = {col["id"]: col["text"] for col in item["column_values"]}
    email = details.get("email", "").strip().lower()
    name = details.get("text6", "") or item["name"]

    if not email or email in emails_sent:
        continue

    try:
        send_email(email, name)
        print(f"📧 Email sent to {email}")
        emails_sent.add(email)
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")
