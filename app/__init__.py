# coding: latin-1
###############################################################################
# Copyright (c) 2023 European Commission
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
###############################################################################

"""
Application Initialization File:
Handles application setup, configuration, and exception handling.
"""

import os, sys
from logging.config import dictConfig

from flask import Flask, render_template
from flask_session import Session
from flask_cors import CORS
from app.app_config.config import ConfigClass
from app.model import keys as keys_service

sys.path.append(os.path.dirname(__file__))

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s | %(module)s (%(funcName)s): %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": "logs/flask.log",
                "when": "D",
                "interval": 7, # a new file for every week
                "backupCount": 5, # the number of files that will be retained on the disk
                "formatter": "default",
            },
        },
        "root": {"level": "INFO", "handlers": ["console", "file"]},
    }
)

def handle_exception():
    return (
        render_template(
            "500.html",
            error="Sorry, an internal server error has occurred. Our team has been notified and is working to resolve the issue. Please try again later.",
            error_code="Internal Server Error",
        ),
        500,
    )

def page_not_found(e):
    return (
        render_template(
            "500.html",
            error_code="Page not found",
            error="Page not found.We're sorry, we couldn't find the page you requested.",
        ),
        404,
    )

def create_app():
    required_certificate = os.path.join(os.getcwd(), ConfigClass.jwt_certificate_path)
    required_key = os.path.join(os.getcwd(), ConfigClass.jwt_private_key_path)
    required_certificate_ca = os.path.join(os.getcwd(), ConfigClass.jwt_ca_certificate_path)
    if not os.path.exists(required_certificate):
        raise FileNotFoundError(f"Critical Error: Required file not found at '{required_certificate}'")
    if not os.path.exists(required_key):
        raise FileNotFoundError(f"Critical Error: Required file not found at '{required_key}'")
    if not os.path.exists(required_certificate_ca):
        raise FileNotFoundError(f"Critical Error: Required file not found at '{required_certificate_ca}'")

    app = Flask(__name__, instance_relative_config=True, static_url_path='/rp/static')
    app.config['SECRET_KEY'] = ConfigClass.secret_key

    # Initialize LoginManager
    from flask_login import LoginManager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from model.user import User
        from model.user_service import UserService
        return User(user_id) if any(user['username'] == user_id for user in UserService.get_users()) else None

    # Register error handlers
    app.register_error_handler(404, page_not_found)

    # Register routes
    from . import (routes)
    app.register_blueprint(routes.rp)
    import model.main.routes as main_routes
    app.register_blueprint(main_routes.base)
    import model.authentication.routes as authentication_routes
    app.register_blueprint(authentication_routes.auth)
    import model.wallet.routes as wallet_interaction_routes
    app.register_blueprint(wallet_interaction_routes.wallet)

    # Configure session    
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_FILE_THRESHOLD"] = 50
    app.config["SESSION_PERMANENT"] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_KEY_PREFIX'] = 'wallet-driven-session:'
    app.config['SESSION_COOKIE_NAME'] = "rp-portal-session"
    app.config['SESSION_COOKIE_PATH'] = '/rp'
    
    app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
    Session(app)

    # Configure CORS
    CORS(app, supports_credentials=True)

    return app