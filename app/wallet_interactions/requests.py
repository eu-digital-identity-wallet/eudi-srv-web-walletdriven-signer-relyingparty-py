import jwt
from app_config.config import ConfService as cfgserv
import uuid
import secrets
import hashlib
import app.wallet_interactions.db as db
from flask import (
    current_app as app, url_for
)

jwt_secret = cfgserv.jwt_secret
jwt_algorithm = cfgserv.jwt_algorithm

# RP generates a Request similar to Authorization Request from [OpenID4VP]
def sd_retrieval_from_authorization_request(document, filename, document_url, hashAlgorithmOID):
    # Obtain the Client Id
    clientId = getClientIdString()
    app.logger.info("Retrieved the client id: "+clientId)

    # "http://127.0.0.1:5001/rp/wallet/sd/upload/"+clientId
    response_uri = url_for('wallet.placeSignedDocument', client_id=clientId, _external=True)
    app.logger.info("Retrieved the response uri: "+response_uri)
    
    # Generate random nonce
    nonce = secrets.token_urlsafe(32)
    app.logger.info("Generated the nonce: "+nonce)
    
    # Get document Digest
    documentDigests = getDocumentDigest(document, filename, hashAlgorithmOID)

    # Get document Locations
    documentLocations = getDocumentLocation(document_url)
    
    # generate Request Object
    request_object = generateRequestObject(clientId, response_uri, nonce, documentDigests, documentLocations, hashAlgorithmOID)
    app.logger.info("Generated the request object: "+request_object)
    
    db.add_to_signer_document_table(clientId, request_object)
    app.logger.info("Added the request object to the database.")
    
    request_uri = url_for('wallet.retrieveSignerDocument', client_id=clientId, _external=True)
    app.logger.info("Generated the request uri: "+request_uri)
    
    link_to_wallet_tester = cfgserv.wallet_url+"?request_uri="+request_uri+"&client_id="+clientId
    app.logger.info("Generated the link to wallet tester: "+link_to_wallet_tester)

    return link_to_wallet_tester, response_uri
 
 
def getClientIdString(): 
    client_id = uuid.uuid4()
    client_id_string = str(client_id)
    return client_id_string

def generateRequestObject(client_id, response_uri, nonce, documentDigests, documentLocations, hashAlgorithmOID):    
    payload = {
        "response_type": "",
        "client_id": client_id,
        "response_mode": "direct_post",
        "response_uri": response_uri,
        "nonce": nonce,
        "signatureQualifier": "eu_eidas_qes",
        "documentDigests": documentDigests,
        "documentLocations": documentLocations,
        "hashAlgorithmOID": hashAlgorithmOID
    }
    token = jwt.encode(payload, jwt_secret, jwt_algorithm)
    
    return token

def getDocumentDigest(document, filename, hash_algorithm_oid):
    if isinstance(document, str):
        document = document.encode('utf-8')
    
    hash_func = hashlib.new("sha256")
    hash_func.update(document)
    
    documentDigests = [
        {
            "hash":hash_func.hexdigest(),
            "label":filename
        }
    ]
    
    return documentDigests

def getDocumentLocation(document_url):
    documentLocations = [
        {
            "uri": document_url,
            "method": {
                "type": "public"
            }
        }
    ]
    return documentLocations