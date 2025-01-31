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
This config.py contains configuration data.
"""

class ConfService:
    secret_key = "secret_here"
    jwt_secret = "jwt_secret_here"
    jwt_algorithm = "jwt_algorithm_here"
    
    service_url = "rp_web_page_here"
    wallet_url = "wallet_endpoint_url_here"
    
    LOAD_FOLDER = 'app/docs' 
    
    db_host = 'localhost'
    db_port = 3306
    db_name = "db_name_here"
    db_user = "db_user_name_here"
    db_password = "db_password_here"