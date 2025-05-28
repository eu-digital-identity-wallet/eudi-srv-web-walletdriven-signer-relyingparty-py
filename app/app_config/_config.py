# coding: latin-1
###############################################################################
# Copyright (c) 2025 European Commission
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

import os

class ConfigClass:
    secret_key = os.getenv("SECRET_KEY") or "secret_here"

    jwt_private_key_path = os.getenv("JWT_PRIVATE_KEY_PATH") or "jwt private key path here"
    jwt_private_key_passphrase = os.getenv("JWT_PRIVATE_KEY_PASSWORD") or "jwt private key passphrase here"
    jwt_certificate_path = os.getenv("JWT_CERTIFICATE_PATH") or "jwt certificate path here"
    jwt_ca_certificate_path = os.getenv("JWT_CA_CERTIFICATE_PATH") or "jwt CA certificate path here"
    jwt_algorithm = "jwt algorithm here"
    
    service_domain = os.getenv("SERVICE_DOMAIN") or "rp domain here"
    service_url = "http://" + service_domain + "/tester/rp"
    wallet_tester_url = "wallet tester endpoint url here"
    pre_registered_client_id = "pre registered client id here"

    LOAD_FOLDER = 'docs'
    
    db_host = 'host.docker.internal' or 'localhost'
    db_port = 3306
    db_name = os.getenv("DB_NAME") or "db name here"
    db_user = os.getenv("DB_USER") or "db user name here"
    db_password = os.getenv("DB_PASSWORD") or  "db password here"