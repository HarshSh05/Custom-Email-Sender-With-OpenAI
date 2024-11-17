from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from email_sender import send_email_task  # Import Celery task for scheduling
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from dotenv import load_dotenv
from celery import Celery
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///email_events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Define the EmailEvent model
class EmailEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)

# Google Sheets Authorization
def load_google_sheet(sheet_url):
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    credentials = Credentials.from_service_account_file('credentials.json', scopes=scopes)
    client = gspread.authorize(credentials)
    sheet = client.open_by_url(sheet_url).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_data():
    sheet_url = request.form.get('sheet_url')
    csv_file = request.files.get('file')
    email_template = request.form.get('email_template')
    data = None

    try:
        # Validate inputs
        if not email_template:
            flash("Please provide an email template.")
            return redirect(url_for('index'))

        if sheet_url:
            data = load_google_sheet(sheet_url)
        elif csv_file:
            data = pd.read_csv(csv_file)
        else:
            flash("Please provide a valid Google Sheets URL or CSV file.")
            return redirect(url_for('index'))

        # Ensure required column exists
        if 'Email' not in data.columns:
            flash("The dataset must include an 'Email' column.")
            return redirect(url_for('index'))

        # Validate email template placeholders
        for placeholder in email_template.split("{"):
            if "}" in placeholder:
                key = placeholder.split("}")[0]
                if key not in data.columns:
                    flash(f"Missing placeholder '{key}' in the dataset.")
                    return redirect(url_for('index'))

        # Process and schedule email sending
        if data is not None:
            for index, row in data.iterrows():
                recipient = row.get('Email')
                if not recipient:
                    flash(f"Row {index + 1} is missing an email address. Skipping.")
                    continue

                try:
                    # Pass dynamic fields to LLM and schedule the email
                    send_email_task.apply_async(
                        args=[recipient, "Custom Email", email_template, row.to_dict()],
                        countdown=index * 5
                    )
                except KeyError as e:
                    flash(f"Row {index + 1}: Missing placeholder for key: {e}. Skipping.")
                    continue

            flash("Emails have been scheduled!")
        else:
            flash("No valid data found.")
    except Exception as e:
        flash(f"An error occurred: {e}")
    
    return redirect(url_for('index'))


@app.route('/event-webhook', methods=['POST'])
def event_webhook():
    try:
        events = request.get_json()
        if not events:
            return "No data received", 400

        for event in events:
            email = event.get("email")
            event_type = event.get("event")
            timestamp = event.get("timestamp")

            # Save to database
            new_event = EmailEvent(email=email, event_type=event_type, timestamp=timestamp)
            db.session.add(new_event)
            db.session.commit()

        return "Webhook received", 200
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return "Error", 500

@app.route('/metrics', methods=['GET'])
def get_metrics():
    # Query the database for event counts
    delivered_count = EmailEvent.query.filter_by(event_type='delivered').count()
    opened_count = EmailEvent.query.filter_by(event_type='open').count()
    bounced_count = EmailEvent.query.filter_by(event_type='bounce').count()
    sent_count = EmailEvent.query.count()

    # Return metrics as JSON
    metrics = {
        'total_sent': sent_count,
        'delivered': delivered_count,
        'opened': opened_count,
        'bounced': bounced_count,
    }
    return jsonify(metrics)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables within the application context
    app.run(debug=True)
