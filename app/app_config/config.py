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
    secret_key = os.getenv("SECRET_KEY")

    jwt_private_key_path = os.getenv("JWT_PRIVATE_KEY_PATH")
    jwt_private_key_password = os.getenv("JWT_PRIVATE_KEY_PASSWORD")
    jwt_certificate_path = os.getenv("JWT_CERTIFICATE_PATH")
    jwt_ca_certificate_path = os.getenv("JWT_CA_CERTIFICATE_PATH")
    jwt_algorithm = "ES256"

    service_domain =  os.getenv("SERVICE_DOMAIN")
    service_url = os.getenv("SERVICE_URL")
    wallet_url = os.getenv("WALLET_URL")
    pre_registered_client_id = os.getenv("SERVICE_DOMAIN")

    LOAD_FOLDER = 'docs'
    
    db_host = os.getenv("DB_HOST")
    db_port = int(os.getenv("DB_PORT"))
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

