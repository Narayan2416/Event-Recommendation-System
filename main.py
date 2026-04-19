import os
from flask import Flask
from app.routes.services import bp as services_bp
from app.routes.auth import bp as auth_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.register_blueprint(services_bp)
app.register_blueprint(auth_bp)

if __name__ == "__main__":
    app.run(debug=True)