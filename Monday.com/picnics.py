import requests
import smtplib
from email.message import EmailMessage
from config import MONDAY_API_KEY, MONDAY_BOARD_ID

# Example: rep -> (email, app_password)
REP_CREDENTIALS = {
    "John Doe": ("johndoe@gmail.com", "your_app_password"),
    "Aimee Wong": ("aimeew@gmail.com", "your_app_password"),
}

MONDAY_HEADERS = {
    "Authorization": MONDAY_API_KEY,
    "Content-Type": "application/json"
}

# Step 1: Fetch items from Monday
def fetch_new_deals():
    query = """
    query ($board_id: [ID!]) {
      boards(ids: $board_id) {
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
    """
    variables = {"board_id": [MONDAY_BOARD_ID]}
    response = requests.post(
        "https://api.monday.com/v2",
        json={"query": query, "variables": variables},
        headers=MONDAY_HEADERS
    )
    data = response.json()
    if "errors" in data:
        raise Exception(f"Monday API Error: {data['errors']}")
    
    return data["data"]["boards"][0]["items"]

# Step 2: Send email via Gmail SMTP
def send_email(from_email, app_password, to_email, client_first_name, rep_name):
    msg = EmailMessage()
    msg["Subject"] = "Thanks for contacting us!"
    msg["From"] = from_email
    msg["To"] = to_email

    body = f"""Hi {client_first_name},

Thank you for contacting us. I am reviewing your event details and will follow up with you soon.

If you have any other details about your event that you'd like to share, just reply here to reach me directly.

{rep_name}
"""
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(from_email, app_password)
        smtp.send_message(msg)
        print(f"✅ Email sent to {to_email} from {from_email}")

# Step 3: Process deals
def process_deals():
    items = fetch_new_deals()
    
    for item in items:
        columns = {col["id"]: col["text"] for col in item["column_values"]}
        status = columns.get("status", "")
        if status.lower() != "deal created":
            continue
        
        client_email = columns.get("email", "")
        client_first_name = columns.get("first_name", "")
        rep_name = columns.get("rep", "")

        if not client_email or not rep_name:
            print(f"⚠️ Missing info for deal '{item['name']}'")
            continue

        creds = REP_CREDENTIALS.get(rep_name)
        if not creds:
            print(f"❌ No email credentials for rep: {rep_name}")
            continue

        send_email(creds[0], creds[1], client_email, client_first_name, rep_name)

# Run it
if __name__ == "__main__":
    try:
        process_deals()
    except Exception as e:
        print(f"❌ Error: {e}")
