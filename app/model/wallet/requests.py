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

import jwt, secrets, hashlib
from model.wallet import db
from app_config.config import ConfigClass as Config
from flask import (
    current_app as app
)
from model import keys as keys_service

jwt_algorithm = Config.jwt_algorithm

# RP generates a Request similar to Authorization Request from [OpenID4VP]
def sd_retrieval_from_authorization_request(documents_info, documents_url, hash_algorithm_oid, wallet_url, client_id_scheme):
    response_type = "sign_response"
    app.logger.info("Retrieved the Response Type Value.")

    # Obtain the client_id
    client_id, client_id_scheme = get_client_id_and_client_id_scheme(client_id_scheme)
    app.logger.info("Retrieved the client id: "+client_id)
    
    # Generate random nonce
    nonce = secrets.token_urlsafe(32)
    app.logger.info("Generated the Nonce: "+nonce)
    
    # Generate response_uri
    response_uri = Config.service_url + "/wallet/sd/upload/" + nonce
    app.logger.info("Retrieved the Response URI value.")
    
    # Get document Digest
    document_digests = get_document_digest(documents_info, hash_algorithm_oid)
    app.logger.info("Generated the Document Digest Value.")

    # Get document Locations
    document_locations = get_document_location(documents_url)
    app.logger.info("Generated the Document Locations Value.")
    
    # generate Request Object
    request_object = generate_request_object(response_type, client_id, client_id_scheme, response_uri, nonce, document_digests, document_locations, hash_algorithm_oid)
    try:
        jar = get_jar_from_request_object(request_object, client_id_scheme)
        app.logger.info("Generated the Request Object Value.")
    except ValueError as e:
        app.logger.error(f"An error was caught while trying to generate a JWT of a Request Object. {e}")
        raise Exception("It was impossible to complete the request, as there was an error generating the JWT.")

    try:
        db.add_to_request_object_to_table(nonce, jar)
        app.logger.info("Added the request object to the database.")
    except ValueError as e:
        app.logger.error(f"An error was caught while trying to save the Request Object to the Database: {e}.")
        raise Exception("It was impossible to complete the request, as there was an error accessing the database.")

    request_uri = Config.service_url + "/wallet/sd/" + nonce
    app.logger.info("Generated the Request Uri Value.")
    
    link_to_wallet = wallet_url+"?request_uri="+request_uri+"&client_id="+client_id
    app.logger.info("Generated the link to wallet: "+link_to_wallet)

    return link_to_wallet, nonce

def get_client_id_and_client_id_scheme(scheme):
    if scheme == "x509_san_dns":
        return Config.service_domain, "x509_san_dns"
    if scheme == "pre-registered":
        return Config.pre_registered_client_id, "pre-registered"

def get_document_digest(documents_info, hash_algorithm_oid):
    digest_oids = {
        "2.16.840.1.101.3.4.2.1": "sha256",
        "2.16.840.1.101.3.4.2.2": "sha384",
        "2.16.840.1.101.3.4.2.3": "sha512"
    }
    hash_name = digest_oids.get(hash_algorithm_oid)
    app.logger.info("Retrieved the hash algorithm name: "+ hash_name +" from oid: "+ hash_algorithm_oid)

    documents_digests = []
    for doc_info in documents_info:
        filename = doc_info["filename"]
        document_base64 = doc_info["document_base64"]
        if isinstance(document_base64, str):
            document_base64 = document_base64.encode('utf-8')

        hash_func = hashlib.new(hash_name)
        hash_func.update(document_base64)

        documents_digests.append({
            "hash": hash_func.hexdigest(),
            "label": filename
        })
        app.logger.info("Calculated Document Digest of the file: " + filename)
    app.logger.info("Formatted the Document Digest with "+str(len(documents_info))+" documents.")
    return documents_digests

def get_document_location(documents_url):
    document_locations = []

    for url in documents_url:
        document_locations.append({
            "uri": url,
            "method": {
                "type": "public"
            }
        })
    app.logger.info("Formatted the Document Locations with "+str(len(documents_url))+" documents.")
    return document_locations

def generate_request_object(response_type, client_id, client_id_scheme, response_uri, nonce, document_digests, document_locations, hash_algorithm_oid):
    payload = {
        "response_type": response_type,
        "client_id": client_id,
        "client_id_scheme": client_id_scheme,
        "response_mode": "direct_post",
        "response_uri": response_uri,
        "nonce": nonce,
        "signatureQualifier": "eu_eidas_qes",
        "documentDigests": document_digests,
        "documentLocations": document_locations,
        "hashAlgorithmOID": hash_algorithm_oid
    }
    app.logger.info("Formatted the Request Object.")
    return payload

def get_jar_from_request_object(request_object, scheme):
    private_key = keys_service.get_jwt_private_key()
    if scheme == "x509_san_dns":
        certificate_chain = []
        leaf_certificate = keys_service.get_jwt_certificate()
        certificate_chain.append(leaf_certificate)
        ca_certificate = keys_service.get_jwt_ca_certificate()
        certificate_chain.append(ca_certificate)
        headers = {"x5c":certificate_chain}
        app.logger.info("Added Certificate Chain to JWT Headers.")
        token = jwt.encode(request_object, private_key, algorithm=jwt_algorithm, headers=headers)
        app.logger.info("Generated a JWT with the Request Object.")
        return token
    elif scheme == "pre-registered":
        token = jwt.encode(request_object, private_key, algorithm=jwt_algorithm)
        app.logger.info("Generated a JWT with the Request Object.")
        return token
    else:
        raise ValueError("The client_id_scheme selected is not supported.")

def retrieve_signed_objects(nonce):
    app.logger.info(f"Checking if the signed data of the request {nonce} is in the DB.")
    try:
        signed_docs_list = db.get_signed_data_object_from_db(nonce)
    except ValueError as e:
        app.logger.error(f"An error was caught while trying to retrieve the Request Object from the Database: {e}.")
        raise Exception("It was impossible to complete the request, as there was an error accessing the database.")

    if signed_docs_list is None:
        app.logger.info(f"Signed Data Object for the request {nonce} isn't in the DB.")
        return None

    app.logger.info(f"Found {len(signed_docs_list)} Signed Data Object for the request {nonce}.")
    return signed_docs_list