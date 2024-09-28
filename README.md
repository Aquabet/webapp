# webapp

## Prerequisites

- **Python 3.10+**
- **Pip**
- **MySQL**
- **Git**

## Environment Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd <webapp>
```

### Step 2: Set Up a Virtual Environment and Install Dependencies

```bash
python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Set the DATABASE_URI in .env file in the root directory:

```env
DATABASE_URI=mysql+mysqlconnector://username:password@localhost:3306/dbname
```

Replace username, password, and dbname with actual database credentials.

## Build and Deploy Instructions

### Step 1: Run the Application

Start the Flask application:

```bash
$env:FLASK_APP = "app.py"
flask run
```

### Step 2: Access the Health Check Endpoint

```bash
curl -vvvv http://localhost:5000/healthz
curl -vvvv -XPUT http://localhost:8080/healthz
curl -v -X GET -d '{"test":"data"}' http://127.0.0.1:5000/healthz
```

### Step 3: Testing Responses

- 200 OK: Database connection is successful.
- 400 Bad Request: Request contains an unexpected payload.
- 405 Method Not Allowed: Request method is not GET.
- 503 Service Unavailable: Database connection failed.
