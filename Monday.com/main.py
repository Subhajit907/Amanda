import logging
from config import LOG_FILE
#from wordpress_client import get_recent_form_entries
#from monday_client import find_contact_by_email, create_contact
from email_utils import send_alert
# from ai_email_generator import generate_follow_up  # Optional

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

def process_leads():
    try:
        leads = get_recent_form_entries()
        for name, email in leads:
            if not email:
                send_alert("Missing email", f"Lead '{name}' has no email.")
                continue

            existing = find_contact_by_email(email)
            if existing:
                logging.info(f"Contact {email} already exists.")
                continue

            create_contact(name, email)
            logging.info(f"Created contact: {name} ({email})")

            # Optional AI email
            # follow_up = generate_follow_up(name)
            # send_email(email, follow_up)

    except Exception as e:
        logging.error(f"Automation failed: {str(e)}")
        send_alert("Automation Error", str(e))

if __name__ == "__main__":
    process_leads()
