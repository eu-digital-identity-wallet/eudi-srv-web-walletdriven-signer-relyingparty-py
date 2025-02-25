import jwt, secrets, hashlib
from model.wallet import db
from app_config.config import ConfigClass as Config
from flask import (
    current_app as app
)
from model import keys as keys_service

jwt_algorithm = Config.jwt_algorithm

# RP generates a Request similar to Authorization Request from [OpenID4VP]
def sd_retrieval_from_authorization_request(document, filename, document_url, hash_algorithm_oid, response_type, wallet_url):
    # Obtain the client_id
    client_id, client_id_scheme = get_client_id_and_client_id_scheme()
    app.logger.info("Retrieved the client id: "+client_id)
    
    # Generate random nonce
    nonce = secrets.token_urlsafe(32)
    app.logger.info("Generated the nonce: "+nonce)
    
    # Generate response_uri
    response_uri = Config.service_url + "/wallet/sd/upload/" + nonce
    app.logger.info("Retrieved the response uri: "+response_uri)
    
    # Get document Digest
    document_digests = get_document_digest(document, filename, hash_algorithm_oid)

    # Get document Locations
    document_locations = get_document_location(document_url)
    
    # generate Request Object
    request_object = generate_request_object(response_type, client_id, client_id_scheme, response_uri, nonce, document_digests, document_locations, hash_algorithm_oid)
    jar = get_jar_from_request_object(request_object)
    app.logger.info("Generated the request object: "+jar)
    
    db.add_to_signer_document_table(nonce, jar)
    app.logger.info("Added the request object to the database.")
    
    request_uri = Config.service_url + "/wallet/sd/" + nonce
    app.logger.info("Generated the request uri: "+request_uri)
    
    link_to_wallet_tester = wallet_url+"?request_uri="+request_uri+"&client_id="+client_id
    app.logger.info("Generated the link to wallet tester: "+link_to_wallet_tester)

    return link_to_wallet_tester, nonce

def get_client_id_and_client_id_scheme():
    return "walletcentric.signer.eudiw.dev", "x509_san_dns"

def get_document_digest(document, filename, hash_algorithm_oid):
    if isinstance(document, str):
        document = document.encode('utf-8')

    hash_func = hashlib.new("sha256")
    hash_func.update(document)

    document_digests = [
        {
            "hash": hash_func.hexdigest(),
            "label": filename
        }
    ]

    return document_digests

def get_document_location(document_url):
    document_locations = [
        {
            "uri": document_url,
            "method": {
                "type": "public"
            }
        }
    ]
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
    return payload

def get_jar_from_request_object(request_object):
    private_key = keys_service.get_jwt_private_key()

    certificate_chain = []
    leaf_certificate = keys_service.get_jwt_certificate()
    certificate_chain.append(leaf_certificate)
    ca_certificate = keys_service.get_jwt_ca_certificate()
    certificate_chain.append(ca_certificate)

    headers = {"x5c":certificate_chain}
    print(headers)

    token = jwt.encode(request_object, private_key, algorithm=jwt_algorithm, headers=headers)
    print(token)
    return token

# Returns a tuple:
def retrieve_signed_objects(nonce):
    app.logger.info("Checking if the signed data is in the DB.")
    signed_docs_list = db.get_signed_data_object_from_db(nonce)
    if signed_docs_list is None:
        app.logger.info("Signed Data Object isn't in the DB.")
        return None
    print(len(signed_docs_list))
    return signed_docs_list