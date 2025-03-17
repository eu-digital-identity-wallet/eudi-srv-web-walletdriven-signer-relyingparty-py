import os
from flask import (Blueprint, render_template)
from app_config.config import ConfigClass as Config

base = Blueprint("index", __name__, url_prefix="/rp")
base.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@base.route('/', methods=['GET'])
def index():
    route_url= Config.service_url + "/tester"
    return render_template('index.html', redirect_url=route_url)
