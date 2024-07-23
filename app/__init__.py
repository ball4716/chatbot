from flask import Flask
from .routes import app as routes_blueprint

def create_app():
    app = Flask(__name__)
    app.register_blueprint(routes_blueprint)
    return app
