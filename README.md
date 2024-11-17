
# Custom email sender with openai




__Overview__\
The __Custom Email Sender application__ allows users to:\
    1. Upload recipient data from Google Sheets or CSV files.\
    2. Use a customizable prompt box to create personalized emails with placeholders.\
    3. Dynamically generate email content using OpenAI's API.\
    4. Schedule and throttle email sending via Celery and Redis.\
    5. Track email delivery statuses (Delivered, Opened, Bounced) using SendGrid.\
    6. View real-time analytics on a user-friendly dashboard.

## Features

* __Data Input__: Supports Google Sheets and CSV files.
* __Dynamic Content__: Generates personalized emails using placeholders and LLMs.
* __Scheduling__: Schedule emails for specific times or throttle sending rates.
* __Real-Time Analytics__: Displays metrics like Total Sent, Delivered, Opened, and Bounced.
* __Delivery Tracking__: Monitors email statuses via SendGrid webhooks.
* __Dashboard__: Provides live updates with progress indicators.
## Setup Instructions
1. __Prerequisites__
* Python 3.10 or later
* Redis server
* A verified SendGrid account
* OpenAI API key
* Google Cloud Service Account credentials (for Google Sheets integration)
2. __Clone the Repository__
```bash
git clone <repository-url>
cd custom-email-sender
```
3. __Create a Virtual Environment__
```bash
python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate     # For Windows
```
4. __Install Dependencies__
```bash
pip install -r requirements.txt
```
5. __Configure Environment Variables__
Create a ```.env``` file in the project root and add the following:
```bash
SENDGRID_API_KEY=<your-sendgrid-api-key>
EMAIL_USER=<your-verified-sendgrid-email>
OPENAI_API_KEY=<your-openai-api-key>
```
6. __Add Google Credentials__
Place your ```credentials.json``` f(Google Cloud Service Account credentials) in the project root.\

7. __Initialize the Database__
```bash
flask db init
flask db migrate
flask db upgrade
```
8. __Start Services__
* Start Redis:
    ```bash
    redis-server
    ```
* Run Flask server:
    ```bash
    flask run

    ```
* Start Celery worker:
    ```bash
    celery -A app.celery worker --loglevel=info
    ```





## Usage Instructions
1. __Access the Application__
* Open a browser and navigate to: ```http://127.0.0.1:5000```
2. __Upload Data__
* __Option 1__: Enter the Google Sheets URL.
* __Option 2__: Upload a CSV file with required columns.
3. __Create a Template__
* Use placeholders like ```{Company Name}```, ```{Location}``` for dynamic replacement.
* Example:
    ```bash
    Hi {Company Name}, welcome to {Location}!
    ```
4. __Send Emails__
* Click "Upload and Send Emails" to queue the tasks.
5. __View Real-Time Metrics__
* Metrics like Total Sent, Delivered, Opened, and Bounced are displayed on the dashboard.
## Project Structure
```bash
custom-email-sender/
│
├── app.py                 # Main Flask application
├── email_sender.py        # Email sending tasks and LLM integration
├── templates/
│   └── index.html         # Frontend template
├── static/
│   └── css/
│       └── style.css      # Styling for the application
├── credentials.json       # Google Sheets credentials (not included in repo)
├── .env                   # Environment variables (not included in repo)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```
## Technical Details
__Libraries Used__
* __Flask__: Web framework for the application.
* __SQLAlchemy__: Database ORM for scheduling and email status tracking.
* __Celery__: Task queue for email scheduling and throttling.
* __Redis__: Message broker for Celery.
* __SendGrid__: ESP for email delivery and tracking.
* __OpenAI API__: LLM for content generation.
__Database__
* SQLite is used to store email statuses and scheduling data.
