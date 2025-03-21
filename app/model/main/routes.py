# coding: latin-1
###############################################################################
# Copyright 2025 European Commission
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

import os
from flask import (Blueprint, render_template)
from app_config.config import ConfigClass as Config

base = Blueprint("index", __name__, url_prefix="/rp")
base.template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template/')

@base.route('/', methods=['GET'])
def index():
    route_url= Config.service_url + "/tester"
    return render_template('index.html', redirect_url=route_url)
