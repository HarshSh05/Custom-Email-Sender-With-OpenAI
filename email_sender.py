from celery import Celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import os
import openai

# Load environment variables from .env file
load_dotenv()

celery = Celery('tasks', broker='redis://localhost:6379/0')

openai.api_key = os.getenv("OPENAI_API_KEY")

@celery.task
def send_email_task(recipient, subject, body_template, dynamic_fields):
    try:
        # Generate email content using OpenAI
        prompt = body_template.format(**dynamic_fields)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        generated_body = response.choices[0].text.strip()

        # Send email using SendGrid
        message = Mail(
            from_email=os.getenv("EMAIL_USER"),
            to_emails=recipient,
            subject=subject,
            plain_text_content=generated_body
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)

        print(f"Email sent to {recipient} with status code {response.status_code}")
        return f"Email sent to {recipient} with status code {response.status_code}"
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")
        return str(e)
