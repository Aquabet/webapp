from flask import Flask, request, jsonify, Response
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, DBAPIError
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DATABASE_URI = os.getenv('DATABASE_URI')
engine = create_engine(DATABASE_URI)

@app.route('/healthz', methods=['GET'])
def health_check():
    # 400 Bad Request
    if request.get_data(as_text=True):
        return jsonify({"error": "Bad Request"}), 400, {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        }
    try:
        # 200 OK
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return jsonify({"status": "healthy"}), 200, {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        }    
    except (OperationalError, DBAPIError) as e:
        # 503 Service Unavailable
        print(f"Database connection failed: {e}")
        return jsonify({"error": "Service Unavailable"}), 503, {
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache"
        }
    
@app.errorhandler(405)
def method_not_allowed(e):
    # 405 Method Not Allowed
    return jsonify({"error": "Method Not Allowed"}), 405, {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache"
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
