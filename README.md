#FluxKart Identity Reconciliation API
This project solves the identity reconciliation problem — identifying and linking customer contacts based on provided email and/or phone number.

🔗 Hosted API
POST /identify

Endpoint: https://fluxcart-identity.onrender.com/identify

Usage

Request
Method: POST
Content-Type: application/json

Body:
{
"email": "john@example.com",
"phoneNumber": "9876543210"
}

Response:
{
"contact": {
"primaryContactId": 1,
"emails": ["john@example.com", "john.1@example.com"],
"phoneNumbers": ["1234567890"],
"secondaryContactIds": [2, 3]
}
}

Tech Stack:
FastAPI – Web framework(Python)
SQLite – Lightweight database (used for easy deployment)
SQLAlchemy – ORM
Pydantic – Data validation
Render.com – Free app hosting

Run Locally
cmd

# Install dependencies

pip install -r requirements.txt

# Run the app

uvicorn main:app --reload
Then open http://localhost:8000/docs to test the API in Swagger UI.

Built for the Bitespeed backend task.
Handles merging of multiple customer records using link precedence logic.
