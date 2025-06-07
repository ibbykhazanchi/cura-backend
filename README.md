# Prescription Management API

A FastAPI-based backend service for managing prescription medications and tracking adherence.

## Features

- User management
- Prescription tracking
- Medication usage logging
- Adherence calculation
- RESTful API endpoints

## Prerequisites

- Python 3.8+
- SQLite3
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pillai-backend
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Database Setup

The application uses SQLite as its database. The database file (`prescriptions.db`) will be created automatically when you first run the application.

## Running the Application

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## API Endpoints

### Users

- `POST /users/` - Create a new user
- `GET /users/{user_id}` - Get user details
- `PUT /users/{user_id}` - Update user details
- `DELETE /users/{user_id}` - Delete a user

### Prescriptions

- `POST /users/{user_id}/prescriptions/` - Create a new prescription
- `GET /users/{user_id}/prescriptions` - Get all prescriptions for a user

### Usage Logs

- `POST /users/{user_id}/usage/` - Log medication usage
- `GET /users/{user_id}/usage/` - Get usage logs
- `GET /users/{user_id}/prescriptions/{prescription_id}/adherence` - Get adherence metrics

## Example Usage

### Create a User
```bash
curl -X POST http://localhost:8000/users/ \
-H "Content-Type: application/json" \
-d '{
    "email": "test@example.com",
    "full_name": "Test User"
}'
```

### Create a Prescription
```bash
curl -X POST http://localhost:8000/users/1/prescriptions/ \
-H "Content-Type: application/json" \
-d '{
    "medication_name": "Amoxicillin",
    "dosage": "500mg",
    "pills_per_dose": 1,
    "times_per_day": 2,
    "start_date": "2024-03-20T00:00:00",
    "end_date": "2024-03-27T00:00:00"
}'
```

### Log Medication Usage
```bash
curl -X POST http://localhost:8000/users/1/usage/ \
-H "Content-Type: application/json" \
-d '{
    "prescription_id": 1,
    "taken_at": "2024-03-20T08:00:00"
}'
```

### Check Adherence
```bash
curl "http://localhost:8000/users/1/prescriptions/1/adherence"
```

## Development

### Running Tests
```bash
pytest
```

### Database Management

To clear all usage logs:
```bash
sqlite3 prescriptions.db "DELETE FROM usage;"
```

## Project Structure

```
pillai-backend/
├── main.py              # FastAPI application and routes
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── database.py          # Database configuration
├── adherence.py         # Adherence calculation logic
├── requirements.txt     # Project dependencies
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here] 