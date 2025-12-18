import os
from dotenv import load_dotenv
import resend

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

try:
    response = resend.Emails.send({
        "from": "JBLB <send@yieldsport.xyz>",
        "to": ["funmilolaslimmy@gmail.com"],  
        "subject": "Test Email",
        "html": "<p>This is a test email</p>"
    })
    print("Email sent successfully!")
    print(response)
except Exception as e:
    print(f"Failed to send email: {str(e)}")