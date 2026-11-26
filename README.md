# URL Shortener & Analytics API

RESTful API built with **Python**, **FastAPI**, and **SQLAlchemy** for shortening URLs, handling HTTP redirects, and tracking real-time click analytics with relational database persistence.

## Tech Stack

- **Python 3.11+**
- **FastAPI** (Web framework & automatic OpenAPI/Swagger documentation)
- **SQLAlchemy & SQLite** (ORM and relational database persistence)
- **Pydantic** (URL validation and data serialization)
- **Pytest & HTTPX** (Automated integration tests with isolated test database)

## API Endpoints

- `POST /shorten` — Validates a target URL and generates a unique 6-character short code (`201 Created` or `422 Unprocessable Entity`).
- `GET /{short_code}` — Redirects (`307 Temporary Redirect`) to the original URL and increments the click counter.
- `GET /stats/{short_code}` — Returns link metadata, creation timestamp, and total click count.
- `DELETE /urls/{short_code}` — Removes a shortened URL record from the database (`204 No Content`).

## Running Locally

```bash
# Clone the repository
git clone https://github.com
cd url-shortener-api

# Create virtual environment and install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```

Interactive Swagger documentation will be available at: `http://localhost:8000/docs`

## Running Automated Tests

```bash
pytest
```
