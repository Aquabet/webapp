# webapp

## CSYE-6225
- [Web Application](https://github.com/Aquabet/webapp)
- [Terraform-Infra](https://github.com/Aquabet/tf-aws-infra)
- [Serverless Lambda](https://github.com/Aquabet/serverless)

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

# for windows
venv\Scripts\activate
# for Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

Set the DATABASE_URI in .env file in the root directory:

```env
DATABASE_URI=mysql+mysqlconnector://username:password@localhost:3306/dbname
```

Replace username, password, and dbname with actual database credentials.

## Build and Deploy Instructions

Start the Flask application:

```bash
# for windows
$env:FLASK_APP = "app.py"
# for linux
export FLASK_APP=app.py
flask run
```

## Health Check Endpoint

```bash
# 200 if everything OK, 503 if database down
curl -vvvv http://localhost:5000/healthz
# 405
curl -vvvv -XPUT http://localhost:5000/healthz
# 400
curl -vvvv http://localhost:5000/healthz?a='3'
# 400
curl -v -X GET -d '{"test":"data"}' http://127.0.0.1:5000/healthz
```

## User management Endpoint

### create user

```bash
# 201 for the first time, run twice to test duplicate create, expected 400
curl -v -X POST http://localhost:5000/v1/user -H "Content-Type: application/json" -d '{
    "email": "li.jiaxia@northeastern.edu",
    "password": "123456",
    "first_name": "Jiaxian",
    "last_name": "Li"
}'

# non-email username, expected 400
curl -v -X POST http://localhost:5000/v1/user -H "Content-Type: application/json" -d '{
    "email": "li.jiaxia.northeastern.edu",
    "password": "123456",
    "first_name": "Jiaxian",
    "last_name": "Li"
}'
```

### get user infomation

```bash
# 200
curl -X GET "http://localhost:5000/v1/user/self" -u "li.jiaxia@northeastern.edu:123456"
# 404
curl -X GET "http://localhost:5000/v1/user/self" -u "li@northeastern.edu:123456"
# 401
curl -X GET "http://localhost:5000/v1/user/self" -u "li.jiaxia@northeastern.edu:12345678"
```

### update user infomation

```bash
# 204
curl -v -u li.jiaxia@northeastern.edu:123456 -X PUT http://localhost:5000/v1/user/self -H "Content-Type: application/json" -d '{
    "first_name": "Jason",
    "last_name": "Lee",
    "password": "12345678"
}'
# updating account_created, expected 400 
curl -v -u li.jiaxia@northeastern.edu:12345678 -X PUT http://localhost:5000/v1/user/self -H "Content-Type: application/json" -d '{
    "first_name": "Jason",
    "last_name": "Lee",
    "password": "12345678",
    "account_created":"Fri, 04 Oct 2024 20:05:26 GMT"
}'
```

## Error Handling

- 400 Bad Request: Returned when there are validation errors such as missing fields or incorrect data formats (e.g., invalid email format).
- 401 Unauthorized: Returned when authentication fails (e.g., wrong email or password).
- 404 Not Found: Returned when the requested resource (e.g., user) is not found.
- 405 Method Not Allowed: Returned when an unsupported HTTP method is used (e.g., PUT on /healthz).
- 503 Service Unavailable: Returned when the application cannot connect to the database.
