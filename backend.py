
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load API key
load_dotenv()


def generate_email(
    purpose,
    tone,
    recipient,
    recipient_name,
    sender_name,
    start_date=None,
    end_date=None,
    production_start_datetime=None
):

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Check your .env file.")

    client = OpenAI(api_key=api_key)

    # Leave date details
    leave_details = ""

    if start_date:
        leave_details += f"\nLeave Start Date: {start_date}"

    if end_date:
        leave_details += f"\nLeave End Date: {end_date}"

    # Production date and time details
    production_details = ""

    if production_start_datetime:
        production_details = f"""
        Proposed Production Start Date and Time:
        {production_start_datetime}
        """

    prompt = f"""
    You are an expert business email writer.

    Generate an email using these details:

    Purpose: {purpose}
    Tone: {tone}
    Recipient Type: {recipient}
    Recipient Name: {recipient_name}
    Sender Name: {sender_name}

    {leave_details}
    {production_details}

    Instructions:
    1. Generate a suitable subject line.
    2. Write a clear and professional email.
    3. Include the leave dates if provided.
    4. If production date and time are provided,
       clearly mention the proposed production start date and time.
    5. Explain the reason for postponement when applicable.
    6. Do not invent dates, times, or personal information.
    7. Do not include the greeting or sender signature in the body.
    8. Avoid placeholders such as [Manager's Name].
    9. Return valid JSON with exactly two fields:
       subject and body.
    10. Return only the JSON object.

    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You generate clear and professional business emails."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.7
    )

    output = response.choices[0].message.content
    email_data = json.loads(output)

    subject = email_data["subject"].strip()
    email_body = email_data["body"].strip()

    # Add greeting and sender signature
    body = f"""Dear {recipient_name},

{email_body}

Thank you for your consideration.

Best regards,
{sender_name}"""

    return {
        "subject": subject,
        "body": body
    }
