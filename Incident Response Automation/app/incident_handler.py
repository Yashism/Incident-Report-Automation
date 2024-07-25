# app/incident_handler.py

import openai
from app.models import db, Resolution, Incident
from app.email_sender import send_email

openai.api_key = 'your-openai-api-key'

def handle_incident(incident):
    # Analyze the incident description using OpenAI
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Analyze this IT incident and provide a solution if possible: {incident.description}",
        max_tokens=150
    )
    
    analysis = response.choices[0].text.strip()
    
    if "CRITICAL" in analysis.upper():
        # Handle critical incident
        incident.priority = 'High'
        db.session.commit()
        notify_admin(incident)
    elif "SOLUTION:" in analysis.upper():
        # Auto-resolve simple incident
        solution = analysis.split("SOLUTION:")[1].strip()
        auto_resolve(incident, solution)
        email_customer(incident, solution)
    else:
        # Unable to auto-resolve, set to medium priority for human review
        incident.priority = 'Medium'
        db.session.commit()

def auto_resolve(incident, resolution_text):
    resolution = Resolution(
        incident_id=incident.id,
        resolution_text=resolution_text
    )
    incident.status = 'Resolved'
    db.session.add(resolution)
    db.session.commit()

def notify_admin(incident):
    admin_email = "admin@company.com"
    subject = f"CRITICAL INCIDENT: #{incident.id}"
    body = f"A critical incident has been reported:\n\nID: {incident.id}\nCustomer: {incident.customer_id}\nDescription: {incident.description}"
    send_email(admin_email, subject, body)

def email_customer(incident, solution):
    subject = f"Resolution for your reported issue: #{incident.id}"
    body = f"Dear Customer,\n\nWe have automatically resolved your reported issue. Here are the steps to fix it:\n\n{solution}\n\nIf you need further assistance, please don't hesitate to contact us."
    send_email(incident.customer_id, subject, body)