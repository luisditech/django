import requests
import logging
from django.template.loader import render_to_string
from django.conf import settings

DEFAULT_CC = "cc@ditech.es"
logger = logging.getLogger(__name__)

def send_email(template_name, context, to, subject, cc=None):
    try:
        html_body = render_to_string(template_name, context)

        payload = {
            "To": to,
            "Cc": cc or DEFAULT_CC,
            "Subject": subject,
            "Body": html_body
        }

        print(f"[DEBUG] Payload: {payload}")
        print(f"[DEBUG] API URL: {settings.EMAIL_API_URL}")

        response = requests.post(settings.EMAIL_API_URL, json=payload, timeout=10)
        response.raise_for_status()

        try:
            response_data = response.json()
        except ValueError:
            response_data = {"raw": response.text}

        return {
            "success": True,
            "message": "Email sent",
            "response": response_data
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send email: {e}")
        return {
            "success": False,
            "message": f"Email sending failed: {str(e)}"
        }