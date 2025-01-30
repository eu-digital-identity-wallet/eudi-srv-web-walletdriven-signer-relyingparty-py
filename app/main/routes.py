import os
from flask import (Blueprint, render_template)
from app_config.config import ConfService as cfgserv

base = Blueprint("index", __name__, url_prefix="/")
base.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@base.route('/', methods=['GET'])
def index():
    return render_template('index.html', redirect_url= cfgserv.service_url)
