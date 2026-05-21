import os
from flask import Flask
from app.services.services import bp as services_bp
from app.routes.auth import bp as auth_bp
from app.routes.routes import bp as routes_bp
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.register_blueprint(services_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(routes_bp)
'''
if __name__ == "__main__":
    app.run(host='0.0.0.0')'''
