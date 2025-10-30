from flask import Flask
from .extensions import ma
from .models import db
from .blueprints.customer import customers_bp

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(f'config.{config_name}')


    # INITIALIZE EXTENSIONS
    ma.init_app(app)
    db.init_app(app)

    # REGISTER BLUEPRINTS
    app.register_blueprint(customers_bp, url_prefix='/customers')

    return app