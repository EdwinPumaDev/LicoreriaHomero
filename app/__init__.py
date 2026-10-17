
from flask import Flask

from config import Config
from app.extensions import db, migrate, login_manager, csrf
from app import models


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.routes.admin import admin
    app.register_blueprint(admin)

    @app.get("/health")
    def health_check():
        return {
            "status": "ok",
            "application": "Licorería Homero",
        }, 200

    return app
